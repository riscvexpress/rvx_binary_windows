# ****************************************************************************
# ****************************************************************************
# Copyright SoC Design Research Group, All rights reserved.
# Electronics and Telecommunications Research Institute (ETRI)
# 
# THESE DOCUMENTS CONTAIN CONFIDENTIAL INFORMATION AND KNOWLEDGE
# WHICH IS THE PROPERTY OF ETRI. NO PART OF THIS PUBLICATION IS
# TO BE USED FOR ANY OTHER PURPOSE, AND THESE ARE NOT TO BE
# REPRODUCED, COPIED, DISCLOSED, TRANSMITTED, STORED IN A RETRIEVAL
# SYSTEM OR TRANSLATED INTO ANY OTHER HUMAN OR COMPUTER LANGUAGE,
# IN ANY FORM, BY ANY MEANS, IN WHOLE OR IN PART, WITHOUT THE
# COMPLETE PRIOR WRITTEN PERMISSION OF ETRI.
# ****************************************************************************
# 2020-03-17
# Kyuseung Han (han@etri.re.kr)
# ****************************************************************************
# ****************************************************************************

include ../rvx_config_python.mh

all: ocd compiler

ocd:
	${PYTHON3_CMD} -c "import glob, tarfile; [tarfile.open(x).extractall('./ocd') for x in glob.glob('./openocd_rvp-*.tar.gz')]"

compiler:
	${PYTHON3_CMD} ./get_xpack_compiler.py -s repack --keeps_archive

clean:
	${PYTHON3_CMD} -c "import shutil; [shutil.rmtree(x, ignore_errors=True) for x in ('./ocd', './compiler_xpack')]"

.PHONY: all ocd compiler clean
