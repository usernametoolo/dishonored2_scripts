from collections import namedtuple, OrderedDict
from pprint import pprint
import types
from tabulate import tabulate 
import math
import os
from pathlib import Path
import pickle
import zlib

from utils import recordclassdef, expectValue
from bindata import BinData


ExportContext = recordclassdef('ExportContext', ['exportRoot', 'gameBasePath'])
MasterRecordBlock0 = recordclassdef('MasterRecordBlock0', ['index', 'res'])
MasterRecordBlock1 = recordclassdef('MasterRecordBlock1', ['file', 'idx'])
MasterRecordBlock2 = recordclassdef('MasterRecordBlock2', ['unk', 'shadersc'])
IndexRecord = recordclassdef('IndexRecord', ['idx', 'type', 'name', 'fileName', 'offset', 'size1', 'size2', 'u0', 'u1', 'u2', 'u3', 'u4'])

print(IndexRecord._fields)

def readString(bd):
    size = bd.readU32()
    # print(size)
    return bd.readStr(size)

def openFile(filePath):
    print('openFile {}'.format(filePath))
    with filePath.open(mode='rb') as f:
        filedata = f.read()
        bd = BinData(filedata)
        print('file size =', bd.dataSize())
        return bd
    return None

def readMasterFile(context, bd):
    print('readMasterFile')
    magic = bd.readBytes(4)
    
    expectValue(magic, b'\x04SER', 'master index file magic')

    print('block #0 0x{:x} ========================'.format(bd.tell()))
    recordFiles = bd.readU16BE()
    recordsCount = bd.readU16BE()
    
    print(recordFiles, recordsCount)

    expectValue(recordFiles, 2, 'block 0 expects 2 files')

    block0 = []
    for rc in range(recordsCount):
        rec = MasterRecordBlock0()
        rec.index = readString(bd)
        rec.res = readString(bd)
        print(rec)
        block0.append(rec)

    print('block #1 0x{:x} ========================'.format(bd.tell()))
    recordFiles = bd.readU16BE()
    recordsCount = bd.readU16BE()
    print(recordFiles, recordsCount)
    expectValue(recordFiles, 0)
    
    block1 = []
    for rc in range(recordsCount):
        rec = MasterRecordBlock1()
        rec.file = readString(bd)
        rec.idx = bd.readU16BE()
        print(rec)

    print('block #2 0x{:x} ========================'.format(bd.tell()))
    block2 = MasterRecordBlock2()
    block2.unk = [bd.readU16BE() for i in range(6)]
    block2.shadersc = readString(bd)
    print(block2)

    expectValue(bd.dataSizeLeft(), 0, "full size is not read")

    return [block0, block1, block2]




def readIndexFile(context, bd):
    print('readIndexFile')

    magic = bd.readBytes(4)
    expectValue(magic, b'\x05SER', 'index file magic')

    dataSize = bd.readU32BE()
    expectValue(dataSize + 0x20, bd.dataSize(), "file size and expected data size don't match")
    bd.seekSet(0x20)

    recordsCount = bd.readU32BE()
    print('recordsCount =', recordsCount)


    records = []

    for ridx in range(recordsCount):
    # for ridx in range(1000):
        rec = IndexRecord()
        rec.idx = bd.readU32BE()
        rec.type = readString(bd)
        rec.name = readString(bd)
        rec.fileName = readString(bd)
        rec.offset = bd.readU64BE()
        rec.size1 = bd.readU32BE()
        rec.size2 = bd.readU32BE()
        rec.u0 = bd.readU16BE()
        rec.u1 = bd.readU16BE()
        rec.u2 = bd.readU16BE()
        rec.u3 = bd.readU16BE()
        rec.u4 = bd.readU16BE()

        records.append(rec)

    expectValue(bd.dataSizeLeft(), 0, "full size is not read")

    return records

def writeIndexTable(context, indexName, records):
    if len(records) > 0:
        headers = records[0]._fields
        tab = tabulate(records, floatfmt='.6', headers=headers)

        outPath = context.exportRoot / (indexName + '.txt')
        with outPath.open('w') as f:
            f.write(tab)
    else:
        print('index is empty')

def exportResourcePak(context, indexRecords, pakName):
    print('exportResourcePak {}'.format(pakName))
    outRoot = context.exportRoot / pakName
    outRoot.mkdir(exist_ok=True, parents=True)

    pakPath = context.gameBasePath / pakName
    
    with pakPath.open(mode='rb') as f:
        for rec in indexRecords:
            name = rec.fileName
            
            if not name:
                if rec.name:
                    name = '__NONAME__/' + rec.name
                else:
                    print('record has no name and filename')
                    continue

            outFilePath = outRoot / name
            outFileDir = outFilePath.parent
            # print(outFileDir)

            f.seek(rec.offset)
            fileData = f.read(rec.size2)


            if rec.size1 != rec.size2:
                try:
                    fileData = zlib.decompress(fileData)
                except zlib.error as err:
                    print('unable to zlib decompress record {} err {}'.format(rec, err))
                    outFilePath = outFilePath.with_name(outFilePath.name + '.archived')    
                pass

            print("{} off 0x{:x} sizes 0x{:x} 0x{:x} -> {}".format(name, rec.offset, rec.size1, rec.size2, outFilePath))
            # expectValue(rec.size1, rec.size2, "sizes don't match for offset {:x}".format(rec.offset))

            outFileDir.mkdir(exist_ok=True, parents=True)
            with outFilePath.open(mode='wb') as outf:
                outf.write(fileData)




def export(context):
    masterPath = context.gameBasePath / 'master.index'
    master = readMasterFile(context, openFile(masterPath))

    blockIdx = 0
    arkIdx = 2

    print('----')
    indexName = master[blockIdx][arkIdx].index
    print(indexName)
    indexPath = context.gameBasePath / indexName

    records = readIndexFile(context, openFile(indexPath))
    writeIndexTable(context, indexName, records)

    print('----')
    pakName = master[blockIdx][arkIdx].res
    exportResourcePak(context, records, pakName)



context = ExportContext()
context.exportRoot = Path(r'e:/dishonored_reverse/out/')
context.gameBasePath = Path(r'd:/SteamLibrary/steamapps/common/Dishonored2/base/')

export(context)