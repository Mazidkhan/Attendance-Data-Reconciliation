#  Copyright (C) VAA Technologies Private Limited - All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by VAA Technologies Private Limited

import os
rpi_user = 'vaa' if os.path.isdir('/home/vaa') else 'pi'

PROD_LOG_PATH = '/home/{}/data-drive/attendance-data-reconciliation/logs'.format(rpi_user)
PROD_CONFIG_PATH = '/home/{}/data-drive/attendance-data-reconciliation/files/config'.format(rpi_user)
PROD_DB_PATH = '/home/{}/data-drive/attendance-data-reconciliation/files/db'.format(rpi_user)

