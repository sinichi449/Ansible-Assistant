#!/usr/bin/env python
# coding: utf-8

import os
import click
import shutil
import subprocess
from utils import device_helpers

device_id = '<your-device-id>'
device_handler = device_helpers.DeviceRequestHandler(device_id)

def show_files_in_dict():
    files_array = sorted(os.listdir())  # sort files into alphabetical
    files_dict = {}
    index_dict = 1
    for i in files_array:
        click.echo(f'{index_dict}. {i}')
        files_dict[index_dict] = i
        index_dict += 1
    return files_dict

def files_operation_dialog():
    click.echo('=' * 55)
    click.echo('Which folder/file?\n')
    click.echo('=' * 55)

current_dir = os.getcwd()
@device_handler.command('com.example.commands.BlinkLight')
def blink(speed, number):
    click.echo(speed)
    click.echo(number)

@device_handler.command('com.example.commands.LSL')
def listAllFiles(folder):
    '''DOWNLOADS, DOCUMENTS, HOME, CURRENT'''
    if folder == "DOWNLOADS":
        click.echo(os.system('ls ~/Downloads -l'))
    elif folder == "DOCUMENTS":
        click.echo(os.system('ls ~/Documents -l'))
    elif folder == "HOME":
        click.echo(os.system('ls ~ -l'))
    elif folder == "CURRENT":
        # show current_dir -> ls {current_dir} -l
        click.echo(os.system(f'ls {current_dir} -l'))
    else:
        click.echo('Not found')

#TP
@device_handler.command('com.example.commands.CD')
def changeDirectory(dir_destination):
    #         if dir_destination == 'previous':
    #             os.chdir('../')
    #         else:
    #             dir_destination = click.prompt('Please type again: ')
    global current_dir
    current_dir = os.getcwd()
#         os.chdir(f'{dir_destination}')
    dir_destination = click.prompt(f'{current_dir}/')
    os.chdir(f'{dir_destination}')

@device_handler.command('com.example.commands.CP')
def copyFiles():
    files_operation_dialog()
    files = show_files_in_dict()

    index_dict = click.prompt('Choose: ')
    dst = click.prompt('Target folder: ')

    shutil.copy2(src=files[int(index_dict)], dst=dst)
    click.echo('Success')

@device_handler.command('com.example.commands.RM')
def removeFiles():
    files_operation_dialog()
    files = show_files_in_dict()

    index_dict = click.prompt('Choose: ')

    confirmation = click.prompt('Are you sure? Y/[N]')
    if confirmation == 'Y' or confirmation == 'y':
        try:
            os.remove(files[int(index_dict)])
        except:
            directory = files[int(index_dict)]
            os.system(f'rm -rf {directory}')
        print('Success')
    else:
        print('Aborted by user.')

@device_handler.command('com.example.commands.MKDIR')
def makeFolder():
    folder_name = input('Folder name: ')
    os.mkdir(folder_name)
    print('Success')

@device_handler.command('com.example.commands.MV')
def moveFile():
    files_operation_dialog()
    files = show_files_in_dict()

    index_dict = input('Choose: ')
    dst = input('Target folder: ')

    shutil.move(src=files[int(index_dict)], dst=dst)
    print('Success')
    
@device_handler.command('com.example.commands.MKDIRRAND')
def createRandomFolder():
    subprocess.call(["./shell/mkdir.sh"])
    print('Success')
    
@device_handler.command('com.example.commands.DMESG')
def logSystem(grep):
    if grep:
        print(f'Executing:\t dmesg --level=err | grep -i {grep}')
        print(f'Recent errors on the {grep}')
        os.system(f'dmesg --level=err | grep -i {grep}')
    else:
        print('Executing:\t dmesg --level=err')
        print('Recent errors of the system')
        os.system('dmesg --level=err')
    
def get_device_handler():
    return device_handler
