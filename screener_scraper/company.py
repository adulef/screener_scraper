# %%
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import json

class Company:
    def __init__(
        self,
        ticker = None, 
        timeout = 2,
        retry = 2,
        path_initial = "https://www.screener.in/company/",
        path_closing = "/consolidated/",
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
            'like Gecko) '
            'Chrome/80.0.3987.149 Safari/537.36',
            'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'},
        debug = True
    ):
        self.path_initial = path_initial
        self.ticker = ticker
        self.path_closing = path_closing
        self.headers = headers
        self.timeout = timeout
        self.retry = retry
        self.debug = debug
        self.soup, self.is_success = self._load(self.debug, self.ticker, self.retry, self.timeout)
        
        if self.is_success:
            self.basic_info = self._get_base_info()
            self.pros_cons = self._get_pros_cons()
            # self.peer_details = self._get_peer_companies()
            self.qoq_res = self._get_qoq_results()
            self.profit_loss = self._get_profit_loss()
            self.bal_sheet = self._get_balance_sheet()
            self.cash_flow = self._get_cash_flow()
            self.ratios = self._get_ratios()
            self.shareholding = self._get_shareholding()
            self.company_id = self._get_company_id()

    def get_basic_info(self):
        return self.basic_info
    
    def get_pros_cons(self):
        return self.pros_cons
    
    # def get_peer_companies(self):
    #     return self.peer_details

    def get_qoq_results(self):
        return self.qoq_res

    def get_profit_loss(self):
        return self.profit_loss
    
    def get_balance_sheet(self):
        return self.bal_sheet
    
    def get_cash_flow(self):
        return self.cash_flow

    def get_ratios(self):
        return self.ratios
    
    def get_shareholding(self):
        return self.shareholding

    def _load(self, debug, ticker, retry, timeout):
        try:
            path = self.path_initial + self.ticker + self.path_closing
            r = requests.get(path, headers=self.headers, timeout= self.timeout)
            
            if retry == 0:
                print("maximum limit exceed: " + ticker) if debug else None
                return None, False
                    
            if r.status_code == 404:
                print("(404) path: " + path) if debug else None
                return None, False
            
            if r.status_code == 429:
                print("(429) cooling for: " + ticker) if debug else None
                time.sleep(timeout)
                return self.load(debug, ticker, retry - 1, timeout)
            # print(r.status_code)
            soup = BeautifulSoup(r.content, 'html.parser')
            print("(success) _load(): " + ticker) if debug else None
            return soup, True
        except:
            print("(err) _load(): " + self.ticker) if self.debug else None
            return None, False


    def _get_base_info(self):
        try:
            name_class = "flex-row flex-wrap flex-align-center flex-grow"
            cname = self.soup.find("div", {"class": name_class}).find("h1").text

            links_class = "company-links show-from-tablet-landscape"
            link_nodes = self.soup.find("div", {"class": links_class}).find_all("a", href=True)
            clink = link_nodes[0]["href"]
            bselink = link_nodes[1]["href"]
            nselink = link_nodes[2]["href"]
            
            primary = [["company_name", cname], ["company_link", clink], 
            ["bse_link", bselink], ["nse_link", nselink]]
            
            secondary = [[str(line.find("span", {"class":"name"}).text).replace("\n", "").strip(), 
                    line.find("span", {"class":"number"}).text]
                        for line in self.soup.find(id="top-ratios").find_all("li")
                ]
            
            df = pd.DataFrame(primary+secondary, columns = ["indicator", "value"])
            df["symbol"] = self.ticker
            
            # print("(success) _get_base_info(): " + self.ticker) if self.debug else None
            return df
        except:
            print("(err) _get_base_info(): " + self.ticker) if self.debug else None
            return None


    def _get_pros_cons(self):
        try:
            pros_lines = self.soup.find("div", {"class": "pros"}).find_all("li")
            pros = pd.DataFrame({"value": [str(line.text).strip() for line in pros_lines]})
            cons_lines = self.soup.find("div", {"class": "cons"}).find_all("li")
            cons = pd.DataFrame({"value": [str(line.text).strip() for line in cons_lines]})
            pros["indicator"] = "pros"
            cons["indicator"] = "cons"
            df = pd.concat([pros, cons])
            df["symbol"] = self.ticker

            # print("(success) _get_pros_cons(): " + self.ticker) if self.debug else None
            return df
        except:
            print("(err) _get_pros_cons(): " + self.ticker) if self.debug else None
            return None
        
            
    # def _get_peer_companies(self):
    #     peer_class = "data-table text-nowrap striped mark-visited"
    #     tab = self.soup.find("div", {"id": "peers-table-placeholder"})
    #     table = tab.find("table",{"class":peer_class})
    #             # table_soup = self.soup.find("table", {"class": peer_class})
    #     # print(pd.read_html(table_soup))
    #     # print(str(tab))
    #     return None
    
    def _get_standered_table(self, id, cls):
        qarter = self.soup.find("section", {"id": id})
        table = qarter.find("table",{"class":cls})
        df_q = pd.read_html(str(table))[0]
        # print(df_q)
        res = pd.melt(df_q, id_vars="Unnamed: 0", value_vars=list(df_q.columns[1:]))
        res = res.rename(columns={"Unnamed: 0": "indicator", "variable": "mmmyyyy"})
        res["symbol"] = self.ticker
        # print(res)
        res["value"] = res.value.astype(
            str).str.replace("%", "").str.replace(
                ",", "").astype(float)
        res["indicator"] = res.indicator.str.strip()
        return res


    def _get_qoq_results(self):
        try:
            res = self._get_standered_table("quarters", 
                            "data-table responsive-text-nowrap")
            res = res[res.indicator != "Raw PDF"]

            # print("(success) _get_qoq_results(): " + self.ticker) if self.debug else None
            return res
        except:
            print("(err) _get_qoq_results(): " + self.ticker) if self.debug else None
            return None
    

    def _get_profit_loss(self):
        try:
            res = self._get_standered_table("profit-loss", 
                            "data-table responsive-text-nowrap")
            
            # print("(success) _get_profit_loss(): " + self.ticker) if self.debug else None
            return res
        except:
            print("(err) _get_profit_loss(): " + self.ticker) if self.debug else None
            return None
    
    
    def _get_balance_sheet(self):
        try:
            res = self._get_standered_table("balance-sheet", 
                            "data-table responsive-text-nowrap")
            
            # print("(success) _get_balance_sheet(): " + self.ticker) if self.debug else None
            return res
        except:
            print("(err) _get_balance_sheet(): " + self.ticker) if self.debug else None
            return None


    def _get_cash_flow(self):
        try:
            res = self._get_standered_table("cash-flow", 
                        "data-table responsive-text-nowrap")
            # print(res)
            # print("(success) _get_cash_flow(): " + self.ticker) if self.debug else None
            return res
        except:
            print("(err) _get_cash_flow(): " + self.ticker) if self.debug else None
            return None
    
    def _get_ratios(self):
        try:
            res = self._get_standered_table("ratios", 
                        "data-table responsive-text-nowrap")
            # print(res)
            # print("(success) _get_ratios(): " + self.ticker) if self.debug else None
            return res
        except:
            print("(err) _get_ratios(): " + self.ticker) if self.debug else None
            return None
    
    def _get_shareholding(self):
        try:
            res = self._get_standered_table("shareholding", 
                        "data-table")
            # print(res)
            # print("(success) _get_shareholding(): " + self.ticker) if self.debug else None
            return res
        except:
            print("(err) _get_shareholding(): " + self.ticker) if self.debug else None
            return None

    def _get_company_id(self):
        try:
            id_elm = self.soup.find("div", {"id":"company-info"})
            return id_elm.get("data-company-id")
            # return "565634"
        except:
            print("(err) _get_company_id(): " + self.ticker) if self.debug else None
            return None
    
    def get_daily_quote(self, days=365, retry=2):
        try:
            initial = "https://www.screener.in/api/company/"
            mid = "/chart/?q=Price-DMA50-DMA200-Volume&days="
            ender = "&consolidated=true"
            req_str = initial + self.company_id + mid + str(days) + ender
            resp = requests.get(req_str, headers=self.headers, timeout= self.timeout)
            if retry == 0:
                print("maximum limit exceed: " + self.ticker) if self.debug else None
                return None, False
                    
            if resp.status_code == 404:
                print("(404) path: " + req_str) if self.debug else None
                return None, False
            
            if resp.status_code == 429:
                print("(429) cooling for: " + self.ticker) if self.debug else None
                time.sleep(self.timeout)
                return self.get_daily_quote(days, retry - 1)

            dct = json.loads(resp.content)
            df = pd.DataFrame(dct.get("datasets")[0].get("values"), 
                            columns=["date", "price"])
            df["volume"] = [x[1] for x in dct.get("datasets")[1].get("values")]
            df["DMA50"] = [x[1] for x in dct.get("datasets")[2].get("values")]
            df["DMA200"] = [x[1] for x in dct.get("datasets")[3].get("values")]
            return df
        except:
            print("(err) get_daily_quote(): " + self.ticker) if self.debug else None
            return None


# %%
# s1 = Company("M&M", timeout=5)

# i = 0
# while i< 30:
#     print("call " + str(i))
#     s1.get_daily_quote()
#     i = i + 1
# s2 = screener_scraper("SUZLON")
# s.get_basic_info()

# %%
