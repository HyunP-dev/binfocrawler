from bs4 import BeautifulSoup
import requests
import click
import pandas as pd

from binfocrawler import *


@click.group()
def cli():
    """
    Bill Infomation System Comment Gathering Program\n
      Author: Hyun Park
    """

@cli.command("info", short_help="Get Information by billId (nosave)")
@click.option("--billid", help="BillId", required=True)
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
@click.option("--billid", help="BillId", required=True)
@click.option("--size", default=-1, help="Amount of comments to collect")
@click.option("--filename", default="", help="File path to save", required=True)
def get(billid, size, filename):
    """
    Collect opinions from Bill Information System.
    """
    print("Crawling...")
    print()
    dataset = pd.DataFrame(get_opinions(billid, size))
    print()
    print(dataset.head())
    if filename == "":
        filename = billid+".csv"
    dataset.to_csv(filename, header=True, index=False)

    pass


if __name__ == '__main__':
    cli()
