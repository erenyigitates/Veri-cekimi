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

# def anaSayfayiAc(driver):
#     driver.get(urun_url)
#     time.sleep(2)

def urlTopla():
    global driver
    global degerlendirme_url  # Şunu eklemeniz şart!
    global soru_cevap_url
    degerlendirme_url=driver.find_element(By.CLASS_NAME,"rvw-cnt").find_element(By.TAG_NAME,"a").get_attribute("href")
    soru_cevap_url=driver.find_element(By.CLASS_NAME,"product-questions").get_attribute("href")


def degerlendirmeSayfasi():
    global driver
    driver.get(degerlendirme_url)
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
        if(len(degerlendirmeObjesi.select_one(".comment-info").select(".comment-info-item"))==3):
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


def dataFrameOlusturma(*args,tip="yorum"):
    if tip=="yorum":
        df=pd.DataFrame({
            "yorumlar":yorumlar,
            "puanlar":puanlar,
            "tarihler":tarihler
        })
    elif tip=="soru":
        df=pd.DataFrame({
            "sorular":sorular
        })
    return df

def dfToExcel(df:pd.DataFrame,isim):
    df.to_excel(f"{isim}.xlsx")

def streamlit_app():
    global urun_url
    global driver
    st.title("Ürün Analizi")
        
    url_input = st.text_input("Lütfen analiz etmek istediğiniz ürünün linkini giriniz:")
    dosya_adi = st.text_input("Lütfen dosyanızın adını giriniz:")
    st.markdown("---")
    if "sayfa_secimi" not in st.session_state:
        st.session_state.sayfa_secimi = None
        

    st.write("Lütfen işlem yapmak istediğiniz bölümü seçiniz:")
    col1,colSpace,col2=st.columns([1,4,1])
    with col1:
        if st.button("Ürün Yorumları", help="Bu buton ürün yorumlarını analiz etmek için kullanılır."):
            st.session_state.sayfa_secimi="yorum"
    with colSpace:
        st.write("")
    with col2:
        if st.button("Soru Cevaplar", help="Bu buton ürün hakkındaki soru ve cevapları analiz etmek için kullanılır."):
            st.session_state.sayfa_secimi="soru_cevap"
    
    st.markdown("---")  # Ayırıcı çizgi ekleyerek butonlar arasında boşluk oluşturur
    
    if st.button("Analiz Et", key="analiz_et_button", use_container_width=True, type="primary"):
        if url_input:
            urun_url = url_input
            st.success("URL başarıyla kaydedildi.")
            with st.spinner("Ürün analiz ediliyor..."):
                driverOlustur()
                driver.get(urun_url)
                time.sleep(2)
                urlTopla()
                if st.session_state.sayfa_secimi=="yorum":
                    #start_time = time.time()
                    degerlendirmeSayfasi()
                    degerlendirmeListesiOlusturma()
                    yorumlar.extend(yorumListesiOlusturma(degerlendirmeObjeleri))
                    puanlar.extend(puanListesiOlusturma(degerlendirmeObjeleri))
                    tarihler.extend(tarihListesiOlusturma(degerlendirmeObjeleri))
                    df=dataFrameOlusturma(yorumlar,puanlar,tarihler)
                    dfToExcel(df,dosya_adi)
                    driver.quit()
                    #end_time = time.time()
                    #execution_time = end_time - start_time
                    #st.write(f"Analiz süresi: {execution_time:.2f} saniye")
                if st.session_state.sayfa_secimi=="soru_cevap":
                    sorucevapSayfasi()
                    sorucevapListesiOlusturma()
                    sorular.extend(soruListesiOlusturma(sorucevapObjeleri))
                    df=dataFrameOlusturma(sorular,tip="soru")
                    dfToExcel(df,dosya_adi)
                    driver.quit()
            st.success("Analiz tamamlandı!")
        
        else:
            st.error("Lütfen geçerli bir URL giriniz!")

streamlit_app()