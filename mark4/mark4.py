import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from typing import List
import pandas as pd
import time
import streamlit as st

chrome_driver_path="/Users/erenates/Drivers/chromedriver"
html_doc=None

yeniYorumlar=[]
yeniTarihler=[]
yeniPuanlar=[]
eskiYorumlar=[]
eskiTarihler=[]
eskiPuanlar=[]

yorumlar=[]
puanlar=[]
tarihler=[]
sorular=[]


urun_puani=None
urun_degerlendirme_sayisi=None
urun_soru_sayisi=None
urun_ismi=None
urun_fiyati=None

urun_url=None
degerlendirme_url=None
soru_cevap_url=None
driver=None

degerlendirmeObjeleri:List[BeautifulSoup]=[]
sorucevapObjeleri:List[BeautifulSoup]=[]

def driverOlustur():
    global driver
    service=Service(chrome_driver_path)
    options=Options()
    options.add_experimental_option("detach",True)
    #options.add_argument("--headless")
    driver=webdriver.Chrome(service=service,options=options)
    return driver


def urlTopla():
    global driver
    global degerlendirme_url  
    global soru_cevap_url
    degerlendirme_url=driver.find_element(By.CLASS_NAME,"rvw-cnt").find_element(By.TAG_NAME,"a").get_attribute("href")
    soru_cevap_url=driver.find_element(By.CLASS_NAME,"product-questions").get_attribute("href")
def urunBilgileriTopla():
    global driver
    global urun_ismi
    global urun_fiyati
    global urun_puani
    global urun_degerlendirme_sayisi
    global urun_soru_sayisi
    html_doc=driver.page_source
    soup=BeautifulSoup(html_doc,"html.parser")
    urun_ismi=soup.select_one(".pr-new-br a").text.strip()+" "+soup.select_one(".pr-new-br span").text.strip()
    urun_fiyati=soup.select_one(".pr-bx-nm.with-org-prc").select_one(".prc-dsc").text.strip()
    urun_puani=soup.find(class_="value").text
    urun_degerlendirme_sayisi=soup.select_one(".total-review-count").text
    urun_soru_sayisi=soup.select_one(".answered-questions-count").text
    

def degerlendirmeSayfasi():
    global driver
    driver.get(degerlendirme_url)
    time.sleep(2)
def yenidenEskiye():
    driver.find_element(By.CLASS_NAME,"selected-container").click()
    time.sleep(1)
    
    dropdownElements = driver.find_element(By.CLASS_NAME,"reviews-dropdown")
    liElements = dropdownElements.find_elements(By.TAG_NAME, "li")
 
    for li in liElements:
        if(li.text.strip()=="Yeniden Eskiye"):
            li.click()
            break
    time.sleep(2)  
def eskidenYeniye():
    driver.find_element(By.CLASS_NAME,"selected-container").click()
    time.sleep(1)
    
    dropdownElements = driver.find_element(By.CLASS_NAME,"reviews-dropdown")
    liElements = dropdownElements.find_elements(By.TAG_NAME, "li")
 
    for li in liElements:
        if(li.text.strip()=="Eskiden Yeniye"):
            li.click()
            break
    time.sleep(2)
def degerlendirmeListesiOlusturma():
    global driver
    degerlendirmeObjeleri.clear()
    eski_yorum_sayisi = 0

    while True:
        yorumlar = driver.find_elements(By.CLASS_NAME, "comment")
        yeni_yorum_sayisi = len(yorumlar)

        if eski_yorum_sayisi == yeni_yorum_sayisi:
            print("tüm yorumlar yüklendi")
            print(f"yüklenen yorum sayısı: {eski_yorum_sayisi}")
            break

        eski_yorum_sayisi = yeni_yorum_sayisi

        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(1.5)

        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_UP)
        time.sleep(1.5)

    html_doc=driver.page_source
    soup=BeautifulSoup(html_doc,"html.parser")
    degerlendirmeObjeleri.extend(soup.select(".reviews .comment"))
def yorumListesiOlusturma(degerlendirmeObjeleri:List[BeautifulSoup]):
    comments=[]

    for degerlendirmeObjesi in degerlendirmeObjeleri:
        comment=degerlendirmeObjesi.select_one(".comment-text p").text
        comments.append(comment)

    return comments    
def puanListesiOlusturma(degerlendirmeObjeleri:List[BeautifulSoup]):
    points=[]
    for degerlendirmeObjesi in degerlendirmeObjeleri:
        point=0
        yildizlar=degerlendirmeObjesi.select_one(".comment-header .comment-rating .ratings.readonly").select(".star-w")
        
        for yildiz in yildizlar:
            doluluk=yildiz.select_one(".full").get("style").split(";")[0].split(":")[1].strip()
            if doluluk=="100%":
                point+=1

        points.append(point)

    return points
def tarihListesiOlusturma(degerlendirmeObjeleri:List[BeautifulSoup]):
    dates=[]
    for degerlendirmeObjesi in degerlendirmeObjeleri:
        if(degerlendirmeObjesi.select_one(".comment-info").select(".comment-info-item")[1].text.strip()=="Elite Üye"):
            date=degerlendirmeObjesi.select_one(".comment-info").select(".comment-info-item")[2].text
            dates.append(date)
        else:
            date=degerlendirmeObjesi.select_one(".comment-info").select(".comment-info-item")[1].text
            dates.append(date)
    return dates


def sorucevapSayfasi():
    driver.get(soru_cevap_url)
    time.sleep(2)
def sorucevapListesiOlusturma():
    eski_sorucevap_sayisi = 0
    sorucevapObjeleri.clear()

    while True:
        sorucevaplar = driver.find_elements(By.CLASS_NAME, "qna-item")
        yeni_sorucevap_sayisi = len(sorucevaplar)

        if eski_sorucevap_sayisi == yeni_sorucevap_sayisi:
            print("tüm yorumlar yüklendi")
            print(f"yüklenen yorum sayısı: {eski_sorucevap_sayisi}")
            break

        eski_sorucevap_sayisi = yeni_sorucevap_sayisi

        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(1.5)

        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_UP)
        # driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_UP)
        # driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_UP)    
        time.sleep(1.5)


    html_doc=driver.page_source
    soup=BeautifulSoup(html_doc,"html.parser")
    sorucevapObjeleri.extend(soup.select(".qna-item"))
def soruListesiOlusturma(sorucevapObjeleri:List[BeautifulSoup]):
    questions=[]
    for sorucevapObjesi in sorucevapObjeleri:
        question=sorucevapObjesi.select_one(".item h4").text
        questions.append(question)
    return questions


def yorumDataFrameOlusturma(yorumlar,puanlar,tarihler):
    df=pd.DataFrame({
        "yorum":yorumlar,
        "puan":puanlar,
        "tarih":tarihler
    })
    df.index = df.index + 1
    return df
def soruDataFrameOlusturma(sorular):
    df=pd.DataFrame({
        "soru":sorular
    })
    df.index = df.index + 1
    return df


def dfToExcel(df:pd.DataFrame,isim,sheet_name):
    df.to_excel(f"{isim}.xlsx",sheet_name=sheet_name)
def dfToExcelSheets(df1:pd.DataFrame,df2:pd.DataFrame,isim):
    with pd.ExcelWriter(f"{isim}.xlsx") as writer:
        df1.to_excel(writer,sheet_name="Yeniden Eskiye")
        df2.to_excel(writer,sheet_name="Eskiden Yeniye")


def streamlit_app():
    global urun_url
    global driver
    st.title("Ürün Analizi")
        
    url_input = st.text_input("Lütfen analiz etmek istediğiniz ürünün linkini giriniz:")
    dosya_adi = st.text_input("Lütfen dosyanızın adını giriniz:")
    st.markdown("---")
    if "sayfa_secimi" not in st.session_state:
        st.session_state.sayfa_secimi = None
    if "filtre_secimi" not in st.session_state:
        st.session_state.filtre_secimi = None
    

    st.write("Lütfen işlem yapmak istediğiniz bölümü seçiniz:")
    col1,col2=st.columns(2)
    with col1:
        if st.button("Ürün Yorumları", help="Bu buton ürün yorumlarını analiz etmek için kullanılır.",use_container_width=True):
            st.session_state.sayfa_secimi="yorum"
    with col2:
        if st.button("Soru Cevaplar", help="Bu buton ürün hakkındaki soru ve cevapları analiz etmek için kullanılır.",use_container_width=True):
            st.session_state.sayfa_secimi="soru_cevap"
    
    st.write("Lütfen filtre seçimi yapınız:")
    col1,col2,col3=st.columns([1,1,1])
    with col1:
        if st.button("Yeniden Eskiye",use_container_width=True):
            st.session_state.filtre_secimi="yeniden_eskiye"
    with col2:
        if st.button("Eskiden Yeniye",use_container_width=True):
            st.session_state.filtre_secimi="eskiden_yeniye"
    
    with col3:
        if st.button("Hepsi",use_container_width=True):
            st.session_state.filtre_secimi="hepsi"
    st.markdown("---")


    if st.button("Analiz Et",use_container_width=True,type="primary"):
        if url_input:
            urun_url = url_input
            st.success("URL başarıyla kaydedildi.")
            with st.spinner("Ürün analiz ediliyor..."):
                driverOlustur()
                driver.get(urun_url)
                time.sleep(2)
                urunBilgileriTopla()
                urlTopla()
                if (st.session_state.sayfa_secimi=="yorum" and st.session_state.filtre_secimi=="yeniden_eskiye"):
                    degerlendirmeSayfasi()
                    yenidenEskiye()
                    degerlendirmeListesiOlusturma()
                    yeniYorumlar.extend(yorumListesiOlusturma(degerlendirmeObjeleri))
                    yeniPuanlar.extend(puanListesiOlusturma(degerlendirmeObjeleri))
                    yeniTarihler.extend(tarihListesiOlusturma(degerlendirmeObjeleri))
                    df1=yorumDataFrameOlusturma(yeniYorumlar,yeniPuanlar,yeniTarihler)
                    dfToExcel(df1,dosya_adi,"Yeniden Eskiye Yorumlar")
                    driver.quit()
                if (st.session_state.sayfa_secimi=="yorum" and st.session_state.filtre_secimi=="eskiden_yeniye"):
                    degerlendirmeSayfasi()
                    eskidenYeniye()
                    degerlendirmeListesiOlusturma()
                    eskiYorumlar.extend(yorumListesiOlusturma(degerlendirmeObjeleri))
                    eskiPuanlar.extend(puanListesiOlusturma(degerlendirmeObjeleri))
                    eskiTarihler.extend(tarihListesiOlusturma(degerlendirmeObjeleri))
                    df2=yorumDataFrameOlusturma(eskiYorumlar,eskiPuanlar,eskiTarihler)
                    dfToExcel(df2,dosya_adi,"Eskiden Yeniye Yorumlar")
                    driver.quit()
                if(st.session_state.sayfa_secimi=="yorum" and st.session_state.filtre_secimi=="hepsi"):
                    degerlendirmeSayfasi()
                    yenidenEskiye()
                    degerlendirmeListesiOlusturma()
                    yeniYorumlar.extend(yorumListesiOlusturma(degerlendirmeObjeleri))
                    yeniPuanlar.extend(puanListesiOlusturma(degerlendirmeObjeleri))
                    yeniTarihler.extend(tarihListesiOlusturma(degerlendirmeObjeleri))
                    df1=yorumDataFrameOlusturma(yeniYorumlar,yeniPuanlar,yeniTarihler)
                    driver.quit()
                    driverOlustur()
                    driver.get(degerlendirme_url)
                    time.sleep(2)
                    eskidenYeniye()
                    degerlendirmeListesiOlusturma()
                    eskiYorumlar.extend(yorumListesiOlusturma(degerlendirmeObjeleri))
                    eskiPuanlar.extend(puanListesiOlusturma(degerlendirmeObjeleri))
                    eskiTarihler.extend(tarihListesiOlusturma(degerlendirmeObjeleri))
                    df2=yorumDataFrameOlusturma(eskiYorumlar,eskiPuanlar,eskiTarihler)
                    dfToExcelSheets(df1,df2,dosya_adi)
                    driver.quit()
                

                if (st.session_state.sayfa_secimi=="soru_cevap" and st.session_state.filtre_secimi=="yeniden_eskiye"):
                    sorucevapSayfasi()
                    yenidenEskiye()
                    sorucevapListesiOlusturma()
                    sorular.extend(soruListesiOlusturma(sorucevapObjeleri))
                    df=soruDataFrameOlusturma(sorular)
                    dfToExcel(df,dosya_adi,"Sorular")
                    driver.quit()

                if (st.session_state.sayfa_secimi=="soru_cevap" and st.session_state.filtre_secimi=="eskiden_yeniye"):
                    sorucevapSayfasi()
                    eskidenYeniye()
                    sorucevapListesiOlusturma()
                    sorular.extend(soruListesiOlusturma(sorucevapObjeleri))
                    df=soruDataFrameOlusturma(sorular)
                    dfToExcel(df,dosya_adi,"Sorular")
                    driver.quit()

                if (st.session_state.sayfa_secimi=="soru_cevap" and st.session_state.filtre_secimi=="hepsi"):
                    sorucevapSayfasi()
                    yenidenEskiye()
                    sorucevapListesiOlusturma()
                    sorular.extend(soruListesiOlusturma(sorucevapObjeleri))
                    df1=soruDataFrameOlusturma(sorular)
                    sorular.clear()
                    driver.quit()
                    driverOlustur()
                    driver.get(soru_cevap_url)
                    time.sleep(2)
                    eskidenYeniye()
                    sorucevapListesiOlusturma()
                    sorular.extend(soruListesiOlusturma(sorucevapObjeleri))
                    df2=soruDataFrameOlusturma(sorular)
                    dfToExcelSheets(df1,df2,dosya_adi)
                    driver.quit()
                    
                    
            st.success("Analiz tamamlandı!")
            print(f"urun ismi: {urun_ismi}")
            print(f"urun fiyati: {urun_fiyati}")
            print(f"urun puanı: {urun_puani}")
            print(f"urun degerlendirme sayisi: {urun_degerlendirme_sayisi}")
            print(f"urun soru sayisi: {urun_soru_sayisi}")
        
        else:
            st.error("Lütfen geçerli bir URL giriniz!")

streamlit_app()