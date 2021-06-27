import click
import pandas as pd
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

def get_html(bill_id: str, size: int) -> str:
    """
    의안정보시스템에서 입법예고 등록의견 페이지를 내보내는 함수

    :param bill_id: 사이트 매개변수
    :param size: 가져올 의견 갯수
    :return: 입법예고 등록의견 HTML
    """
    url = "http://likms.assembly.go.kr/bill/nacom/nacomList.do"

    payload = f'billId={bill_id}&pageSize={size}'
    headers = {
        'Accept': 'text/html, */*; q=0.01',
        'DNT': '1',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text


def get_data(bill_id: str, size: int) -> list:
    """
    의안정보시스템에서 입법예고 등록의견을 수집해 내보내는 함수

    :param bill_id: 사이트 매개변수
    :param size: 가져올 의견 갯수 (-1인 경우, 모든 의견을 가져옮.)
    :return: 입법예고 등록의견 데이터
    """
    if size == -1:
        size = get_last_index(bill_id)

    url = "http://likms.assembly.go.kr/bill/nacom/nacomList.do"

    payload = f'billId={bill_id}&pageSize={size}'
    headers = {
        'Accept': 'text/html, */*; q=0.01',
        'DNT': '1',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    bs = BeautifulSoup(response.text, "html5lib")
    trs = bs.select("#commentListArea > div > table > tbody > tr")

    result = []
    element = {}
    for i in tqdm(range(0, len(trs))):
        if element == {}:
            element = {}
            if i % 2 == 0:
                tds = trs[i].select("td")
                element["id"] = int(tds[0].text.strip())
                element["author"] = tds[2].text.strip()
                element["group"] = tds[3].text.strip()
                element["date"] = tds[4].text.strip()
        else:
            element["title"] = trs[i].select("td > div > p")[0].text.strip()[5:]
            element["content"] = trs[i].select("td > div > div")[0].text.strip().replace("\n", "").replace("\r", "")
            if set(element.keys()) == {"id", "title", "author", "group", "date", "content"}:
                result.append(element)
            element = {}
    return result


def get_last_index(bill_id: str) -> int:
    """
    등록된 의견의 갯수를 내보내는 함수

    :param bill_id: 사이트 매개변수
    :return: 등록된 의견의 갯수
    """
    url = "http://likms.assembly.go.kr/bill/nacom/nacomList.do"

    payload = f'billId={bill_id}'
    headers = {
        'Accept': 'text/html, */*; q=0.01',
        'DNT': '1',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    bs = BeautifulSoup(response.text, "html.parser")
    return int(bs.find('input', {"type": "hidden", "name": "allCount"})["value"])

@click.group()
def cli():
    """
    Bill Infomation System Comment Gathering Program\n
      Author: Hyun Park
    """

@cli.command("info", short_help="Get Information by billId (nosave)")
@click.option("--billid", help="BillId")
def info(billid):
    """
    Print an information for a bill corresponding to billId
    """
    url = f"https://likms.assembly.go.kr/bill/billDetail.do?billId={billid}"
    bs = BeautifulSoup(requests.get(url).text, "html5lib")
    
    title = ("["+str(bs.select("h3.titCont")[0]).split("<span")[0].split("[")[1]).strip()
    level = bs.select("div.stepType01 > span.on")[0].text.strip()
    
    number = bs.select("div.tableCol01 > table > tbody > tr > td:nth-child(1)")[0].text.strip()
    date = bs.select("div.tableCol01 > table > tbody > tr > td:nth-child(2)")[0].text.strip()
    proposers = bs.select("div.tableCol01 > table > tbody > tr > td:nth-child(3)")[0].text.replace("&nbsp;", " ").strip()
    nth = bs.select("div.tableCol01 > table > tbody > tr > td:nth-child(5)")[0].text.strip()
    
    print(title)
    print()
    print("심사진행단계:", level)
    print()									
    print("의안번호:", number)
    print("제안일자:", date)
    print("제안자  :", proposers)
    print("제안회기:", nth)
    print()
    content = bs.select("#summaryContentDiv")[0]
    print("\n".join(list(map(lambda e:e.strip(), str(content).split("<br/>")))[1:]).replace("</div>","").strip())

@cli.command("get", short_help="Get Comments by billId")
@click.option("--billid", help="BillId")
@click.option("--size", default=-1, help="Amount of comments to collect")
@click.option("--filename", default="", help="File path to save")
def get(billid, size, filename):
    """
    Collect opinions from Bill Information System.
    """
    print("Crawling...")
    print()
    dataset = pd.DataFrame(get_data(billid, size))
    print()
    print(dataset.head())
    if filename == "":
        filename = billid+".csv"
    dataset.to_csv(filename, header=True, index=False)

    pass


if __name__ == '__main__':
    cli()
