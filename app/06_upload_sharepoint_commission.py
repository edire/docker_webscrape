#%%

import os
import pandas as pd
from ddb.sql import SQL
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
import dlogging

logger = dlogging.NewLogger(__file__, use_cd=True)
directory = os.path.dirname(__file__)
filepath_commissions = os.path.join(directory, 'commissions.xlsx')


#%%

logger.info('Get Commission Proc Input Data')
con = SQL()
df = con.read('EXEC dbo.stpCommission_Input')


#%%

logger.info('Load Workbook')

with pd.ExcelWriter(filepath_commissions, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
    df.to_excel(writer, index=False, header=False, sheet_name='Sheet1', startrow=3)


#%%

logger.info('Sharepoint Authentication')
url = os.getenv('sharepoint_url')
ctx_auth = AuthenticationContext(url)
ctx_auth.acquire_token_for_app(os.getenv('sharepoint_client_id'), os.getenv('sharepoint_client_secret'))
ctx = ClientContext(url, ctx_auth)


#%%

logger.info('Upload to sharepoint')
target_folder = ctx.web.get_folder_by_server_relative_url(os.getenv('sharepoint_upload_folder'))

with open(filepath_commissions, 'rb') as content_file:
    file_content = content_file.read()
    target_folder.upload_file('Commission_Approvals.xlsx', file_content).execute_query()


logger.info('Upload complete!')


#%%