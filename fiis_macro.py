# %%
# Importa bibliotecas
import pandas as pd, requests, time, numpy as np
from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime
# %%
# Pega o ticker de todos os FIIs e agrupa em uma lista
headers = {
    'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36'
        ' (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
}

url = f'https://www.fundamentus.com.br/fii_resultado.php'
fiis_tickers = []
response = requests.get(url, headers=headers)

if response.status_code == 200:
  response = response.content
  data = BeautifulSoup(response, 'html.parser')

for linha in data.find_all('a'):
  if '11' in linha.text:
    if '11B' not in linha.text:
      fiis_tickers.append(linha.text)
# %%
# Utiliza lista de tickers e faz o webscrapping para pegar as informações dos FIIs
df = pd.DataFrame(
    columns=[
        'COD',
        'Provento',
        'Liq Diaria',
        'Patr Liq',
        'Valor Patr',
        'Publico Alvo',
        'Segmento',
        'Mandato',
        'Cotas Emitidas'
    ]
)
#fiis_tickers = fiis_tickers[0:10]
ticket_falha = []
for cod, i in zip(fiis_tickers, tqdm(range(len(fiis_tickers) - 1))):

  provento = np.nan
  liq_diaria = np.nan
  patr_liq = np.nan
  val_patr = np.nan
  publ = np.nan
  segm = np.nan
  mand = np.nan
  cots = np.nan

  try:
    url = f'https://www.fundsexplorer.com.br/funds/{cod}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
      response = response.content
      data = BeautifulSoup(response, 'html.parser')
    #dados fundamentos
    info_fii = data.find_all(class_='indicators__box')
    #proventos
    try:
      raw_div = info_fii[1].text
      provento = float(raw_div.replace('Último Rendimento', '').replace('R$', '').replace('.', '').replace('\n', '').replace('\t', '').replace(',', '.'))
      if provento == 'N/A':
        provento = ''
    except:
      provento = ''
    #liquidez diaria
    try:
      raw_liq_diaria = info_fii[0].text
      if 'K' in raw_liq_diaria:
        liq_diaria = float(raw_liq_diaria.replace('\nLiquidez Média Diária\n', '').replace(' K', '').replace(',', '.').replace('\n', '').replace('\t', '')) * 1000
      else:
        liq_diaria = float(raw_liq_diaria.replace('\nLiquidez Média Diária\n', '').replace(' M', '').replace(',', '.').replace('\n', '').replace('\t', '')) * 1000000

    except:
      liq_diaria = ''
    #patrimonio liquido
    try:
      raw_patr_liq = info_fii[3].text
      if ' K' in raw_patr_liq:
        patr_liq = float(raw_patr_liq.replace('Patrimônio Líquido', '').replace('R$', '').replace(' K', '').replace(',', '.').replace('\n', '').replace('\t', '')) * 1000
      elif ' M' in raw_patr_liq:
        patr_liq = float(raw_patr_liq.replace('Patrimônio Líquido', '').replace('R$', '').replace(' M', '').replace(',', '.').replace('\n', '').replace('\t', '')) * 1000000
      elif ' B' in raw_patr_liq:
        patr_liq = float(raw_patr_liq.replace('Patrimônio Líquido', '').replace('R$', '').replace(' B', '').replace(',', '.').replace('\n', '').replace('\t', '')) * 1000000000
    except:
      patr_liq = ''

    #valor patrimonial
    try:
      raw_val_patr = info_fii[4].text
      val_patr = int(raw_val_patr.replace('\nValor Patrimonial', '').replace('R$', '').replace('por cota', '').replace('\n', '').replace(',', '').strip())
    except:
      val_patr = ''
    #basic_info
    basic_info = data.find_all(class_ = 'basicInformation__grid__box')
    for c in range(0, len(basic_info)):
      basic = basic_info[c].text
      if 'Público alvo' in basic:
        publ = basic.split('\n')[2]
      if 'Segmento' in basic:
        segm = basic.split('\n')[2]
      if 'Mandato' in basic:
        mand = basic.split('\n')[2]
      if 'Cotas emitidas' in basic:
        cots = int(basic.split('\n')[2].replace('.', ''))
    #insere dados no  dataframe
    df.loc[df.shape[0]] = [
        cod,
        provento,
        liq_diaria,
        patr_liq,
        val_patr,
        publ,
        segm,
        mand,
        cots
    ]
  except:
    ticket_falha.append(cod)
# %%
df.head()
# %%
# To do
# [] Checar necessidade de tratar os dados
# [] Colocar dados no google sheets
# [] Deixar automatizado para rodar 1x por dia
# %%
#import os.path
#
#from google.auth.transport.requests import Request
#from google.oauth2.credentials import Credentials
#from google_auth_oauthlib.flow import InstalledAppFlow
#from googleapiclient.discovery import build
#from googleapiclient.errors import HttpError
#
## If modifying these scopes, delete the file token.json.
#SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
#
## The ID and range of a sample spreadsheet.
#SAMPLE_SPREADSHEET_ID = "1x6-Uzyspp4qL6IKj5zYon3xYZnE7DhNsj3y4-5tUTOo"
#6 = "Base FIIs!A2"
#
#
#def main():
#  """Shows basic usage of the Sheets API.
#  Prints values from a sample spreadsheet.
#  """
#  creds = None
#  if os.path.exists("token.json"):
#    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
#  if not creds or not creds.valid:
#    if creds and creds.expired and creds.refresh_token:
#      creds.refresh(Request())
#    else:
#      flow = InstalledAppFlow.from_client_secrets_file(
#          "credentials.json", SCOPES
#      )
#      creds = flow.run_local_server(port=0)
#    with open("token.json", "w") as token:
#      token.write(creds.to_json())
#
#  try:
#    service = build("sheets", "v4", credentials=creds)
#
#    # Call the Sheets API
#    value_add = df.values.tolist()
#
#    sheet = service.spreadsheets()
#    result = (
#        sheet.values()
#        .update(spreadsheetId=SAMPLE_SPREADSHEET_ID
#                , range=SAMPLE_RANGE_NAME
#                ,valueInputOption='USER_ENTERED'
#                ,body={'values': value_add}
#        )
#        .execute()
#    )
#    values = result.get("values", [])
#    print(values)
#  except HttpError as err:
#    print(err)
#
#
#if __name__ == "__main__":
#  main()
## %%