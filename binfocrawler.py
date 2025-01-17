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
    info = get_info(billid)
    print()
    print(info.title)
    print()
    print("심사진행단계:", info.level)							
    print("의안번호:", info.number)
    print("제안일자:", info.date)
    print("제안자  :", info.proposers)
    print("제안회기:", info.nth)
    print()
    print(info.content)

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
