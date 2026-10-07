## ****************************************************************************
## ****************************************************************************
## Copyright SoC Design Research Group, All rights reserved.    
## Electronics and Telecommunications Research Institute (ETRI)
##
## THESE DOCUMENTS CONTAIN CONFIDENTIAL INFORMATION AND KNOWLEDGE 
## WHICH IS THE PROPERTY OF ETRI. NO PART OF THIS PUBLICATION IS 
## TO BE USED FOR ANY OTHER PURPOSE, AND THESE ARE NOT TO BE 
## REPRODUCED, COPIED, DISCLOSED, TRANSMITTED, STORED IN A RETRIEVAL 
## SYSTEM OR TRANSLATED INTO ANY OTHER HUMAN OR COMPUTER LANGUAGE, 
## IN ANY FORM, BY ANY MEANS, IN WHOLE OR IN PART, WITHOUT THE 
## COMPLETE PRIOR WRITTEN PERMISSION OF ETRI.
## ****************************************************************************
## 2026-09-07
## ****************************************************************************
## ****************************************************************************

import os
import sys
import platform
import zipfile
import argparse
from pathlib import Path

RVX_UTIL_HOME = Path(os.environ.get('RVX_UTIL_HOME', Path(__file__).resolve().parent.parent / 'rvx_util'))
assert RVX_UTIL_HOME.is_dir(), RVX_UTIL_HOME
sys.path.insert(0, str(RVX_UTIL_HOME))

from os_util import *

DEFAULT_VERSION = '15.2.0-1'
RELEASE_URL_FORMAT = 'https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases/download/v{version}/{filename}'
INFO_FILENAME = 'compiler_xpack_info.txt'

class XpackCompiler():
  def __init__(self, version:str=DEFAULT_VERSION):
    assert version
    self.version = version
    self.filename = f'xpack-riscv-none-elf-gcc-{version}-{XpackCompiler.__get_platform()}{XpackCompiler.__get_extension()}'
    self.link = RELEASE_URL_FORMAT.format(version=version, filename=self.filename)

  # e.g., linux-x64, linux-arm64, darwin-x64, darwin-arm64, win32-x64
  @staticmethod
  def __get_platform():
    system = platform.system()
    machine = platform.machine().lower()

    if system=='Linux':
      os_name = 'linux'
    elif system=='Darwin':
      os_name = 'darwin'
    elif system=='Windows':
      os_name = 'win32'
    else:
      assert 0, f'unsupported os: {system}'

    if machine in ('x86_64', 'amd64', 'x64'):
      arch = 'x64'
    elif machine in ('aarch64', 'arm64'):
      arch = 'arm64'
    else:
      assert 0, f'unsupported machine: {platform.machine()}'

    # only x64 is released for windows
    assert not (os_name=='win32' and arch!='x64'), f'unsupported target: {os_name}-{arch}'
    return f'{os_name}-{arch}'

  @staticmethod
  def __get_extension():
    return '.zip' if platform.system()=='Windows' else '.tar.gz'

  @staticmethod
  def __extract(target_file:Path):
    assert target_file.is_file(), target_file
    if target_file.name.endswith('.zip'):
      with zipfile.ZipFile(target_file) as zip_file:
        zip_file.extractall(target_file.parent)
    else:
      extract_file(target_file)

  # the archive holds a single top directory (e.g., xpack-riscv-none-elf-gcc-15.2.0-1)
  @staticmethod
  def __move_up_top_dir(output_dir:Path):
    top_dir_list = [x for x in output_dir.iterdir() if x.is_dir()]
    assert len(top_dir_list)==1, top_dir_list
    top_dir = top_dir_list[0]
    for object in top_dir.iterdir():
      if object.is_file():
        move_files(object, output_dir/object.name)
      elif object.is_dir():
        move_directory(object, output_dir/object.name)
      else:
        assert 0, object
    remove_directory(top_dir)

  def download(self, output_dir:Path, removes_top_dir:bool=True, keeps_archive:bool=False):
    assert output_dir.is_absolute()
    current_link = ''
    current_info_file = output_dir / INFO_FILENAME
    if current_info_file.is_file():
      current_link = current_info_file.read_text().split('\n')[0]

    if self.link!=current_link:
      remove_directory(output_dir)
      output_dir.mkdir(parents=True)
      output_file = output_dir / self.filename
      print(f'Downloading {self.link}')
      download_url(self.link, output_file=output_file)
      XpackCompiler.__extract(output_file)
      if not keeps_archive:
        remove_file(output_file)
      if removes_top_dir:
        XpackCompiler.__move_up_top_dir(output_dir)
      current_info_file.write_text(f'{self.link}\n')
      print('Downloaded')
    else:
      print('No update')

if __name__ =='__main__':
  parser = argparse.ArgumentParser(description='Get xPack RISC-V GCC Toolchain')
  parser.add_argument('-output', '-o', default='./compiler_xpack', help='output directory')
  parser.add_argument('-version', '-v', default=DEFAULT_VERSION, help='xpack release version')
  parser.add_argument('--keeps_top_dir', action='store_true', help='keep the top directory of the archive')
  parser.add_argument('--keeps_archive', action='store_true', help='keep the downloaded archive file')

  args = parser.parse_args()
  output_dir = Path(args.output).absolute().resolve()
  compiler = XpackCompiler(args.version)
  compiler.download(output_dir, not args.keeps_top_dir, args.keeps_archive)
