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
#from google import genai
import google.generativeai as genai
from openai import OpenAI
import tiktoken
import io

chrome_driver_path="/Users/erenates/Drivers/chromedriver"
html_doc=None
maps_html_doc=None
yorum_cekilecek_yer=None
maps_degerlendirme_objeleri:List[BeautifulSoup]=[]
maps_filtrelenmemis_degerlendirme_objeleri:List[BeautifulSoup]=[]
maps_soru_cevap_objeleri=[]
maps_sorular=[]
maps_cevaplar=[]
maps_degerlendirme_yorumlari=[]
maps_degerlendirme_puanlari=[]
maps_degerlendirme_yanitlari=[]
maps_degerlendirme_isimleri=[]
maps_degerlendirme_tarihleri=[]
maps_sorular=[]
maps_cevaplar=[]

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
bilgiler_listesi=[]
urun_ozellikleri=[]

urun_puani=None
urun_degerlendirme_sayisi=None
urun_soru_sayisi=None
urun_yorum_sayisi=None
urun_ismi=None
urun_fiyati=None
urun_bilgileri=[]
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
    #options.add_argument("--start-maximized")

    driver=webdriver.Chrome(service=service,options=options)
    #driver.set_window_size(1200, 650)

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
    global urun_bilgileri
    global urun_yorum_sayisi
    global urun_ozellikleri
    urun_ozellikleri2=[]
    urun_bilgileri2=[]
    
    html_doc=driver.page_source
    soup=BeautifulSoup(html_doc,"html.parser")
    if len(soup.select(".pr-new-br span"))>1:
        urun_ismi=soup.select(".pr-new-br span")[0].text.strip()+" "+soup.select(".pr-new-br span")[1].text.strip()
    else:
        urun_ismi=soup.select_one(".product-brand-name-with-link").text.strip()+" "+soup.select(".pr-new-br span")[0].text.strip()

    urun_fiyati=soup.select_one(".pr-bx-nm.with-org-prc").select_one(".prc-dsc").text.strip()
    urun_puani=soup.find(class_="value").text
    urun_degerlendirme_sayisi=int(soup.select_one(".total-review-count").text)
    urun_yorum_sayisi=int(soup.select_one(".p-reviews-comment-count").text.split(" ")[0])
    urun_soru_sayisi=int(soup.select_one(".answered-questions-count").text)

    urun_bilgi_bolumu=soup.select_one(".detail-desc-list").select("li")[5:]
    for urun_bilgi in urun_bilgi_bolumu:
        urun_bilgi_yazisi=urun_bilgi.text
        urun_bilgileri2.append(urun_bilgi_yazisi)
    urun_bilgileri.append("-".join(urun_bilgileri2))

    urunOzellikleri=soup.select(".detail-attr-container .detail-attr-item")
    for urunOzelligi in urunOzellikleri:
        keydegeri=urunOzelligi.select_one(".attr-name.attr-key-name-w")
        valueDegeri=urunOzelligi.select_one("span[title]")
        if keydegeri and valueDegeri:
            keydegeri = keydegeri.string.strip()
            valueDegeri = valueDegeri.get("title").strip()
            urun_ozellikleri2.append(f"{keydegeri}:{valueDegeri}")
    urun_ozellikleri.append(" - ".join(urun_ozellikleri2))
    

    

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
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_UP)
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
def bedenBoyKilo(degerlendirmeObjeleri:List[BeautifulSoup]):
    global bilgiler_listesi
    bilgiler_listesi.clear()
    for degerlendirmeObjesi in degerlendirmeObjeleri:
        bilgiler={"boy":None,"kilo":None,"beden":None}
        comment_info_items=degerlendirmeObjesi.select(".comment-info-item")
        for item in comment_info_items:
            b_tag=item.find("b")
            if b_tag:
                label=b_tag.get_text(strip=True).lower()

                if b_tag.next_sibling:
                    value = b_tag.next_sibling.strip()
                else:
                    value = None

                if "beden" in label:
                    bilgiler["beden"] = value
                elif "boy" in label:
                    bilgiler["boy"] = value
                elif "kilo" in label:
                    bilgiler["kilo"] = value            
        bilgiler_listesi.append(bilgiler)




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
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_UP)
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_UP)    
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


def yorumDataFrameOlusturma(yorumlar,puanlar,tarihler,bilgiler_listesi):
    df=pd.DataFrame({
        "yorum":yorumlar,
        "puan":puanlar,
        "tarih":tarihler,
        "boy-kilo-beden":bilgiler_listesi
    })
    df.index = df.index + 1
    return df
def soruDataFrameOlusturma(sorular):
    df=pd.DataFrame({
        "soru":sorular
    })
    df.index = df.index + 1
    return df
def bilgiDataFrameOlusturma(urun_ismi,urun_fiyati,urun_puani,urun_degerlendirme_sayisi,urun_yorum_sayisi,urun_soru_sayisi,urun_bilgileri,urun_ozellikleri):
    df=pd.DataFrame({
        "ürün ismi":urun_ismi,
        "ürün fiyatı":urun_fiyati,
        "ürün puanı":urun_puani,
        "ürün değerlendirme sayısı":urun_degerlendirme_sayisi,
        "ürün yorum sayısı":urun_yorum_sayisi,
        "ürün soru sayısı":urun_soru_sayisi,
        "ürün bilgileri":urun_bilgileri,
        "ürün özellikleri":urun_ozellikleri
    })
    df.index = df.index + 1
    return df

def dfToExcel(df:pd.DataFrame,isim,sheet_name):
    df.to_excel(f"{isim}.xlsx",sheet_name=sheet_name)    
def dfToExcelSheets(df1:pd.DataFrame,df2:pd.DataFrame,isim):
    with pd.ExcelWriter(f"{isim}.xlsx") as writer:
        df1.to_excel(writer,sheet_name="Yeniden Eskiye")
        df2.to_excel(writer,sheet_name="Eskiden Yeniye")


#maps fonksiyonları
def mapsDriverOlustur():
    global driver
    service=Service(chrome_driver_path)
    options=Options()
    options.add_experimental_option("detach",True)
    driver=webdriver.Chrome(service=service,options=options)
    return driver   

def mapsDriverOlusturSC():
    global driver
    service=Service(chrome_driver_path)
    options=Options()
    options.add_experimental_option("detach",True)
    driver=webdriver.Chrome(service=service,options=options)
    driver.get(yorum_cekilecek_yer)
    time.sleep(3)
    return driver  
     
def mapsDegerlendirmeYukleme():
    eski_degerlendirme_sayisi=0
    driver.get(yorum_cekilecek_yer)
    time.sleep(1)
    driver.find_elements(By.CSS_SELECTOR, ".hh2c6")[1].click()
    time.sleep(1)
    #istedigimiz yerin yorumlar bolumundeyiz suan
    scroll_div = driver.find_element(By.CSS_SELECTOR, ".m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde")

    while True:
        degerlendirmeler=driver.find_elements(By.CSS_SELECTOR,".jftiEf.fontBodyMedium")
        yeni_degerlendirme_sayisi=len(degerlendirmeler)

        if eski_degerlendirme_sayisi==yeni_degerlendirme_sayisi:
            break

        eski_degerlendirme_sayisi=yeni_degerlendirme_sayisi
        scroll_div.send_keys(Keys.END)
        time.sleep(1.75)

    #yuklenen butun yorumlarin daha falza tusuna bastirmak gerekiyor
    butonlar=driver.find_elements(By.CSS_SELECTOR, ".w8nwRe.kyuRq")
    for buton in butonlar:
        driver.execute_script("arguments[0].click();", buton) #ekranda olmayan butonlarada click yapabilir
        
    html_doc=driver.page_source
    soup=BeautifulSoup(html_doc,"html.parser")
    maps_filtrelenmemis_degerlendirme_objeleri.extend(soup.select(".jftiEf.fontBodyMedium"))
    
    for x in maps_filtrelenmemis_degerlendirme_objeleri:
        if x.select_one(".MyEned .wiI7pd"):
            maps_degerlendirme_objeleri.append(x)
    #degerlendirme_objeleri isimli listede suan butun degerlendirmeler var, icinden gerekli bilgiler cekilecek

def mapsYorumlariYuklemek():
    for degerlendirme_objesi in maps_degerlendirme_objeleri:
        degerlendirme_yorumu=degerlendirme_objesi.select_one(".MyEned .wiI7pd")
        if degerlendirme_yorumu:
            degerlendirme_yorumu=degerlendirme_yorumu.text
        else:
            degerlendirme_yorumu="None"
        maps_degerlendirme_yorumlari.append(degerlendirme_yorumu)
    #eger yorum yoksa None yazdirmasini soyledik, yorum varsada yorumu cekiyor

def mapsYanitlariYuklemek():
    for degerlendirme_objesi in maps_degerlendirme_objeleri:
        degerlendirme_yaniti=degerlendirme_objesi.select_one(".CDe7pd .wiI7pd")
        if degerlendirme_yaniti:
            degerlendirme_yaniti=degerlendirme_yaniti.text
        else:
            degerlendirme_yaniti='None'
        maps_degerlendirme_yanitlari.append(degerlendirme_yaniti)
    #eger yanit yoksa None yazdirmasini soyledik, yanit varsada yorumu cekiyor

def mapsPuanlariYuklemek():
    for degerlendirme_objesi in maps_degerlendirme_objeleri:
        puan=degerlendirme_objesi.select_one(".kvMYJc")["aria-label"]
        maps_degerlendirme_puanlari.append(puan)
        
def mapsIsimleriYuklemek():
    for degerlendirmeobjesi in maps_degerlendirme_objeleri:
        degerlendirme_isimi=degerlendirmeobjesi.select_one(".d4r55").text
        maps_degerlendirme_isimleri.append(degerlendirme_isimi)

def mapsGuneCevir(metin):
    if "yıl" in metin:
        sayi = int(metin.split()[0])
        return sayi * 365
    
    elif "ay" in metin:
        sayi = int(metin.split()[0])
        return sayi * 30
    
    elif "hafta" in metin:
        sayi = int(metin.split()[0])
        return sayi * 7
    
    elif "gün" in metin:
        sayi = int(metin.split()[0])
        return sayi
    
    elif "saat" in metin:
        return 1
      
    elif "dakika" in metin:
        return 1 
    
def mapsTarihleriYuklemek():
    for degerlendirmeobjesi in maps_degerlendirme_objeleri:
        degerlendirme_tarihi=degerlendirmeobjesi.select_one(".rsqaWe").text
        if degerlendirme_tarihi.lower().startswith("bir"):
            degerlendirme_tarihi = degerlendirme_tarihi.replace("bir", "1")
        gun=mapsGuneCevir(degerlendirme_tarihi)
        yeni_degerlendirme_tarihi=f'{gun} gün önce'
        maps_degerlendirme_tarihleri.append(yeni_degerlendirme_tarihi)

def mapsSoruCevapYuklemek():
    global maps_soru_cevap_objeleri
    driver.find_elements(By.CSS_SELECTOR, ".hh2c6")[1].click()
    time.sleep(1)
    driver.find_elements(By.CSS_SELECTOR, ".hh2c6")[0].click()
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, "button[aria-label='Diğer sorular']").click()
    time.sleep(1)
    driver.refresh()
    time.sleep(1)
    body=driver.find_element(By.CLASS_NAME,'.w6VYqd')
    body.send_keys(Keys.PAGE_DOWN)
    time.sleep(1)

    # soru_cevap_html_doc=driver.page_source
    # soup=BeautifulSoup(soru_cevap_html_doc,"html.parser")

    # maps_soru_cevap_objeleri = driver.find_elements(By.CSS_SELECTOR, ".Wde6Oe")
    # for soru_cevap_objesi in maps_soru_cevap_objeleri:
    #     soru=soru_cevap_objesi.find_element(By.CSS_SELECTOR,".NXtIPd").text
    #     cevap=soru_cevap_objesi.find_element(By.CSS_SELECTOR,".Uz0Pqe").text
    #     maps_sorular.append(soru)
    #     maps_cevaplar.append(cevap)
    st.write(driver.find_element(By.CSS_SELECTOR,'DIFKq'))
    
    



    


def streamlit_app():
    global urun_ismi
    global urun_fiyati
    global urun_puani
    global urun_degerlendirme_sayisi
    global urun_yorum_sayisi
    global urun_soru_sayisi
    global urun_bilgileri
    global urun_url
    global driver
    st.image("logo.jpg")
    tab1,tab2,tab3=st.tabs(["Trendyol Veri Çekimi","Veri Analizi","Google Maps Veri Çekimi"])
    with tab1:
        st.title("Trendyol Veri Çekimi")
        url_input = st.text_input("Lütfen analiz etmek istediğiniz ürünün linkini giriniz:")
        dosya_adi = st.text_input("Dosyanızı hangi isimle kayıt etmek istersiniz ?")
        st.markdown("---")
        if "sayfa_secimi" not in st.session_state:
            st.session_state.sayfa_secimi = None
        if "filtre_secimi" not in st.session_state:
            st.session_state.filtre_secimi = None
        

        st.write("Lütfen yapmak istediğiniz işlemi seçiniz:")
        col1,col2=st.columns(2)
        with col1:
            if st.button("Ürün Yorumları",use_container_width=True):
                st.session_state.sayfa_secimi="yorum"
        with col2:
            if st.button("Soru Cevaplar",use_container_width=True):
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


        if st.button("Veri Çekimini Başlat",use_container_width=True,type="primary"):
            if url_input:
                urun_url = url_input
                st.success("URL başarıyla kaydedildi.")
                with st.spinner("Ürün analiz ediliyor..."):
                    driverOlustur()
                    driver.get(urun_url)
                    time.sleep(2)
                    urunBilgileriTopla()
                    urlTopla()
                    bilgi_df=bilgiDataFrameOlusturma(urun_ismi,urun_fiyati,urun_puani,urun_degerlendirme_sayisi,urun_yorum_sayisi,urun_soru_sayisi,urun_bilgileri,urun_ozellikleri)
                    
                    if (st.session_state.sayfa_secimi=="yorum" and st.session_state.filtre_secimi=="yeniden_eskiye"):
                        if(int(urun_yorum_sayisi)<=3030):
                            st.write(f"tahmini bekleme süreniz: {(int(urun_yorum_sayisi)//10)*1.35:.0f} saniye")
                        else:
                            st.write(f"tahmini bekleme süreniz: 420 saniye")
                        degerlendirmeSayfasi()
                        yenidenEskiye()
                        degerlendirmeListesiOlusturma()
                        bedenBoyKilo(degerlendirmeObjeleri)
                        yeniYorumlar.extend(yorumListesiOlusturma(degerlendirmeObjeleri))
                        yeniPuanlar.extend(puanListesiOlusturma(degerlendirmeObjeleri))
                        yeniTarihler.extend(tarihListesiOlusturma(degerlendirmeObjeleri))
                        df1=yorumDataFrameOlusturma(yeniYorumlar,yeniPuanlar,yeniTarihler,bilgiler_listesi)
                        
                        with pd.ExcelWriter(f"{dosya_adi}.xlsx") as writer:
                            df1.to_excel(writer, sheet_name="Yeniden Eskiye Yorumlar")
                            bilgi_df.to_excel(writer, sheet_name="Ürün Bilgileri")
                        driver.quit()
                        
                    if (st.session_state.sayfa_secimi=="yorum" and st.session_state.filtre_secimi=="eskiden_yeniye"):
                        if(int(urun_yorum_sayisi)<=3030):
                            st.write(f"tahmini bekleme süreniz: {(int(urun_yorum_sayisi)//10)*1.35:.0f} saniye")
                        else:
                            st.write(f"tahmini bekleme süreniz: 420 saniye")
                        degerlendirmeSayfasi()
                        eskidenYeniye()
                        degerlendirmeListesiOlusturma()
                        bedenBoyKilo(degerlendirmeObjeleri)
                        eskiYorumlar.extend(yorumListesiOlusturma(degerlendirmeObjeleri))
                        eskiPuanlar.extend(puanListesiOlusturma(degerlendirmeObjeleri))
                        eskiTarihler.extend(tarihListesiOlusturma(degerlendirmeObjeleri))
                        df2=yorumDataFrameOlusturma(eskiYorumlar,eskiPuanlar,eskiTarihler,bilgiler_listesi)
                        with pd.ExcelWriter(f"{dosya_adi}.xlsx") as writer:
                            df2.to_excel(writer, sheet_name="Eskiden Yeniye Yorumlar")
                            bilgi_df.to_excel(writer, sheet_name="Ürün Bilgileri")
                        driver.quit()

                    if(st.session_state.sayfa_secimi=="yorum" and st.session_state.filtre_secimi=="hepsi"):
                        if(int(urun_yorum_sayisi)<=3030):
                            st.write(f"tahmini bekleme süreniz: {(int(urun_yorum_sayisi)//10)*2.7:.0f} saniye")
                        else:
                            st.write(f"tahmini bekleme süreniz: 840 saniye")
                        degerlendirmeSayfasi()
                        yenidenEskiye()
                        degerlendirmeListesiOlusturma()
                        bedenBoyKilo(degerlendirmeObjeleri)
                        yeniYorumlar.extend(yorumListesiOlusturma(degerlendirmeObjeleri))
                        yeniPuanlar.extend(puanListesiOlusturma(degerlendirmeObjeleri))
                        yeniTarihler.extend(tarihListesiOlusturma(degerlendirmeObjeleri))
                        df1=yorumDataFrameOlusturma(yeniYorumlar,yeniPuanlar,yeniTarihler,bilgiler_listesi)
                        driver.quit()
                        driverOlustur()
                        driver.get(degerlendirme_url)
                        time.sleep(2)
                        eskidenYeniye()
                        degerlendirmeListesiOlusturma()
                        bedenBoyKilo(degerlendirmeObjeleri)
                        eskiYorumlar.extend(yorumListesiOlusturma(degerlendirmeObjeleri))
                        eskiPuanlar.extend(puanListesiOlusturma(degerlendirmeObjeleri))
                        eskiTarihler.extend(tarihListesiOlusturma(degerlendirmeObjeleri))
                        df2=yorumDataFrameOlusturma(eskiYorumlar,eskiPuanlar,eskiTarihler,bilgiler_listesi)
                        with pd.ExcelWriter(f"{dosya_adi}.xlsx") as writer:
                            df1.to_excel(writer, sheet_name="Yeniden Eskiye Yorumlar")
                            df2.to_excel(writer, sheet_name="Eskiden Yeniye Yorumlar")
                            bilgi_df.to_excel(writer, sheet_name="Ürün Bilgileri")
                        driver.quit()
                    

                    if (st.session_state.sayfa_secimi=="soru_cevap" and st.session_state.filtre_secimi=="yeniden_eskiye"):
                        if(int(urun_soru_sayisi)<=3030):
                            st.write(f"tahmini bekleme süreniz: {(int(urun_soru_sayisi)//10)*1.35:.0f} saniye")
                        else:
                            st.write(f"tahmini bekleme süreniz: 420 saniye")
                        sorucevapSayfasi()
                        yenidenEskiye()
                        sorucevapListesiOlusturma()
                        sorular.extend(soruListesiOlusturma(sorucevapObjeleri))
                        df=soruDataFrameOlusturma(sorular)
                        with pd.ExcelWriter(f"{dosya_adi}.xlsx") as writer:
                            df.to_excel(writer, sheet_name="Sorular")
                            bilgi_df.to_excel(writer, sheet_name="Ürün Bilgileri")
                        driver.quit()

                    if (st.session_state.sayfa_secimi=="soru_cevap" and st.session_state.filtre_secimi=="eskiden_yeniye"):
                        if(int(urun_soru_sayisi)<=3030):
                            st.write(f"tahmini bekleme süreniz: {(int(urun_soru_sayisi)//10)*1.35:.0f} saniye")
                        else:
                            st.write(f"tahmini bekleme süreniz: 420 saniye")
                        sorucevapSayfasi()
                        eskidenYeniye()
                        sorucevapListesiOlusturma()
                        sorular.extend(soruListesiOlusturma(sorucevapObjeleri))
                        df=soruDataFrameOlusturma(sorular)
                        with pd.ExcelWriter(f"{dosya_adi}.xlsx") as writer:
                            df.to_excel(writer, sheet_name="Sorular")
                            bilgi_df.to_excel(writer, sheet_name="Ürün Bilgileri")
                        driver.quit()

                    if (st.session_state.sayfa_secimi=="soru_cevap" and st.session_state.filtre_secimi=="hepsi"):
                        if(int(urun_soru_sayisi)<=3030):
                            st.write(f"tahmini bekleme süreniz: {(int(urun_soru_sayisi)//10)*2.7:.0f} saniye")
                        else:
                            st.write(f"tahmini bekleme süreniz: 840 saniye")
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
                        with pd.ExcelWriter(f"{dosya_adi}.xlsx") as writer:
                            df1.to_excel(writer, sheet_name="Yeniden Eskiye Sorular")
                            df2.to_excel(writer, sheet_name="Eskiden Yeniye Sorular")
                            bilgi_df.to_excel(writer, sheet_name="Ürün Bilgileri")
                        driver.quit()

            else:
                st.error("Lütfen geçerli bir URL giriniz!")




    with tab2:
        aiYorumAnalizleri=[]
        aiYorumAnalizleriOnizleme=[]
        toplamOpenAIInputTokeni=0
        toplamOpenAIOutputTokeni=0
        
        

        st.title("Veri Analizi")
        yuklenmis_dosya=st.file_uploader("Excel dosyasını yükleyiniz",type=["xlsx"])
        sablon_df = pd.DataFrame(columns=["yorum", "puan", "tarih", "boy-kilo-beden"])

        sablon_df.index=sablon_df.index+1

        excel_buffer = io.BytesIO()
        sablon_df.to_excel(excel_buffer, index=True)
        excel_buffer.seek(0)
        if yuklenmis_dosya is None:
            st.download_button(
                label="Örnek excel şablonunu indir",
                data=excel_buffer,
                file_name=f"uygun_sablon.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        if yuklenmis_dosya is not None:
            df=pd.read_excel(yuklenmis_dosya)
            st.success("Dosya başarıyla yüklendi")
            

            if "yorum" in df.columns:
                analizEdilecekYorumlar=df["yorum"].astype(str).tolist()
                yorumSayisi=len(analizEdilecekYorumlar)
                st.info(f"Toplam yorum sayısı: {yorumSayisi}")

                if "llmmodeli" not in st.session_state:
                    st.session_state.llmmodeli=None
                st.write("Model seçimi yapın:")
                col1,col2=st.columns(2)
                with col1:
                    if st.button("OpenAI"):
                        st.session_state.llmmodeli="openai"
                with col2:
                    if st.button("Gemini"):
                        st.session_state.llmmodeli="gemini"



                if st.session_state.llmmodeli=="openai":

                    kullaniciAPIKey=st.text_input("API Key: ")
                    client = OpenAI(
                        #api_key=kullaniciAPIKey
                        api_key=kullaniciAPIKey
                        )
                    kullaniciPromptu=st.text_area("Prompt:")

                    #token hesabi
                    enc=tiktoken.encoding_for_model("gpt-4o-mini")
                    toplamInputYorumTokeni=sum(len(enc.encode(yorum))for yorum in analizEdilecekYorumlar)
                    toplamInputPromptTokeni=len(enc.encode(kullaniciPromptu)) * yorumSayisi
                    toplamOpenAIInputTokeni=toplamInputYorumTokeni+toplamInputPromptTokeni

                    

                    if st.button("Önizleme ve Maliyet Hesaplama"):
                        onizlemeYapilacakYorumlar=[]
                        analizEdilecekYorumlarSorted=sorted(analizEdilecekYorumlar,key=len)
                        kisayorumlar=analizEdilecekYorumlarSorted[10:12]
                        ortayorumlar=analizEdilecekYorumlarSorted[(yorumSayisi//2)-1:(yorumSayisi//2)+1]
                        uzunyorumlar=analizEdilecekYorumlarSorted[-12:-10]

                        onizlemeYapilacakYorumlar=kisayorumlar+ortayorumlar+uzunyorumlar
                        for onizlemeYapilacakYorum in onizlemeYapilacakYorumlar:
                            full_prompt=f"Yorum: {onizlemeYapilacakYorum}\n\n{kullaniciPromptu}"
                            completion = client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[{"role": "user", "content": full_prompt}]
                            )
                            response=completion.choices[0].message.content
                            aiYorumAnalizleriOnizleme.append(response)
                            
                        onizlemeDF=pd.DataFrame({
                            "Veri":onizlemeYapilacakYorumlar,
                            "İșlenmiş Veri":aiYorumAnalizleriOnizleme
                        })
                        outputTokeni=(sum(len(enc.encode(output)) for output in aiYorumAnalizleriOnizleme))//6
                        toplamOpenAIOutputTokeni=outputTokeni*yorumSayisi
                        st.session_state.toplamOpenAIInputTokeni = toplamOpenAIInputTokeni
                        st.session_state.toplamOpenAIOutputTokeni = toplamOpenAIOutputTokeni
                        st.table(onizlemeDF)


                    if "toplamOpenAIInputTokeni" in st.session_state and "toplamOpenAIOutputTokeni" in st.session_state:
                        st.write(f"Maksimum kullanılacak input tokeni: {st.session_state.toplamOpenAIInputTokeni}")
                        st.write(f"Maksimum kullanılacak output tokeni: {st.session_state.toplamOpenAIOutputTokeni}")

                    if "analizHazir" not in st.session_state:
                        st.session_state.analizHazir=False
                    

                    if st.button("Analiz"):
                        st.session_state.analizHazir=True

                    if st.session_state.analizHazir:
                        
                        analizSayisi=st.text_input("Kaç yorum analiz edilsin ? (Bir şey yazmazsanız hepsi analiz edilecektir)")
                        if st.button("Analiz Et"):
                            if analizSayisi:
                                analizSayisi=int(analizSayisi)
                                yeniAnalizEdilecekYorumlar=analizEdilecekYorumlar[:analizSayisi]
                                yeniDF=df.iloc[:analizSayisi].copy()
                                for analizEdilecekYorum in yeniAnalizEdilecekYorumlar:
                                    full_prompt=f"Yorum: {analizEdilecekYorum}\n\n{kullaniciPromptu}"
                                    

                                    completion = client.chat.completions.create(
                                        model="gpt-4o-mini",
                                        messages=[{"role": "user", "content": full_prompt}]
                                    )

                                    response=completion.choices[0].message.content
                                    aiYorumAnalizleri.append(response)
                                 
                                yeniDF["Yapay Zeka Yorumu"]=aiYorumAnalizleri
                                if "Unnamed: 0" in yeniDF.columns:
                                    yeniDF = yeniDF.drop(columns=["Unnamed: 0"])
                                yeniDF.to_excel(f"{yuklenmis_dosya.name[:-5]}_v2.xlsx", index=True)
                                st.success("Güncellenmiş Excel dosyası başarıyla oluşturuldu")

                            else:
                                for analizEdilecekYorum in analizEdilecekYorumlar:
                                    full_prompt=f"Yorum: {analizEdilecekYorum}\n\n{kullaniciPromptu}"
                                    

                                    completion = client.chat.completions.create(
                                        model="gpt-4o-mini",
                                        messages=[{"role": "user", "content": full_prompt}]
                                    )

                                    response=completion.choices[0].message.content
                                    aiYorumAnalizleri.append(response)
                                df["Yapay Zeka Yorumu"]=aiYorumAnalizleri
                                df.to_excel(f"{yuklenmis_dosya.name[:-5]}_v2.xlsx", index=False)
                                st.success("Güncellenmiş Excel dosyası başarıyla oluşturuldu")

                            


                        


                if st.session_state.llmmodeli=="gemini":
                    kullaniciAPIKey=st.text_input("API Key: ")
                    genai.configure(api_key="kullaniciAPIKey")
                    model=genai.GenerativeModel("gemini-2.0-flash-lite")
                    kullaniciPromptu=st.text_area("Prompt:")

                    #token hesabi
                    enc=tiktoken.encoding_for_model("gpt-4o-mini")
                    toplamInputYorumTokeni=sum(len(enc.encode(yorum))for yorum in analizEdilecekYorumlar)
                    toplamInputPromptTokeni=len(enc.encode(kullaniciPromptu)) * yorumSayisi
                    toplamOpenAIInputTokeni=toplamInputYorumTokeni+toplamInputPromptTokeni

                    if st.button("Önizleme ve Maliyet Hesaplama"):
                        onizlemeYapilacakYorumlar=[]
                        analizEdilecekYorumlarSorted=sorted(analizEdilecekYorumlar,key=len)
                        kisayorumlar=analizEdilecekYorumlarSorted[10:12]
                        ortayorumlar=analizEdilecekYorumlarSorted[(yorumSayisi//2)-1:(yorumSayisi//2)+1]
                        uzunyorumlar=analizEdilecekYorumlarSorted[-12:-10]

                        onizlemeYapilacakYorumlar=kisayorumlar+ortayorumlar+uzunyorumlar
                        for onizlemeYapilacakYorum in onizlemeYapilacakYorumlar:
                            full_prompt=f"Yorum: {onizlemeYapilacakYorum}\n\n{kullaniciPromptu}"
                            response=model.generate_content(full_prompt)
                            response=response.text
                            aiYorumAnalizleriOnizleme.append(response)

                        onizlemeDF=pd.DataFrame({
                            "Veri":onizlemeYapilacakYorumlar,
                            "İșlenmiş Veri":aiYorumAnalizleriOnizleme
                        })
                        outputTokeni=(sum(len(enc.encode(output)) for output in aiYorumAnalizleriOnizleme))//6
                        toplamOpenAIOutputTokeni=outputTokeni*yorumSayisi
                        st.table(onizlemeDF)
                        st.session_state.toplamGeminiInputTokeni = toplamOpenAIInputTokeni*1.25
                        st.session_state.toplamGeminiOutputTokeni = toplamOpenAIOutputTokeni*1.25

                    if "toplamGeminiInputTokeni" in st.session_state and "toplamGeminiOutputTokeni" in st.session_state:
                        st.write(f"Maksimum kullanılacak input tokeni: {st.session_state.toplamGeminiInputTokeni:.0f}")
                        st.write(f"Maksimum kullanılacak output tokeni: {st.session_state.toplamGeminiOutputTokeni:.0f}")

                    if "analizHazir" not in st.session_state:
                        st.session_state.analizHazir=False

                    if st.button("Analiz"):
                        st.session_state.analizHazir=True

                    if st.session_state.analizHazir:
                        analizSayisi=st.text_input("Kaç yorum analiz edilsin ? (Bir şey yazmazsanız hepsi analiz edilecektir)")
                        if st.button("Analiz Et"):
                            if analizSayisi:
                                analizSayisi=int(analizSayisi)
                                yeniAnalizEdilecekYorumlar=analizEdilecekYorumlar[:analizSayisi]
                                yeniDF=df.iloc[:analizSayisi].copy()
                                for analizEdilecekYorum in yeniAnalizEdilecekYorumlar:
                                    full_prompt=f"Yorum: {analizEdilecekYorum}\n\n{kullaniciPromptu}"
                                    response=model.generate_content(full_prompt)
                                    response=response.text
                                    aiYorumAnalizleri.append(response)
                                 
                                yeniDF["Yapay Zeka Yorumu"]=aiYorumAnalizleri
                                if "Unnamed: 0" in yeniDF.columns:
                                    yeniDF = yeniDF.drop(columns=["Unnamed: 0"])
                                yeniDF.to_excel(f"{yuklenmis_dosya.name[:-5]}_v2.xlsx", index=True)
                                st.success("Güncellenmiş Excel dosyası başarıyla oluşturuldu")

                            else:
                                for analizEdilecekYorum in analizEdilecekYorumlar:
                                    full_prompt=f"Yorum: {analizEdilecekYorum}\n\n{kullaniciPromptu}"
                                    response=model.generate_content(full_prompt)
                                    response=response.text
                                    aiYorumAnalizleri.append(response)
                                df["Yapay Zeka Yorumu"]=aiYorumAnalizleri
                                df.to_excel(f"{yuklenmis_dosya.name[:-5]}_v2.xlsx", index=False)
                                st.success("Güncellenmiş Excel dosyası başarıyla oluşturuldu")
            
            
            
            
            else:
                st.error("Excel dosyanız uygun formatta değildir. Aşağıdaki şablonu indirip verilerinizi aktarınız.")

                sablon_df = pd.DataFrame(columns=["yorum", "puan", "tarih", "boy-kilo-beden"])

                sablon_df.index=sablon_df.index+1

                excel_buffer = io.BytesIO()
                sablon_df.to_excel(excel_buffer, index=True)
                excel_buffer.seek(0)

                st.download_button(
                    label="Örnek excel şablonunu indir",
                    data=excel_buffer,
                    file_name=f"uygun_sablon.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )      
    with tab3:
        global yorum_cekilecek_yer
        st.title("Google Maps Veri Çekimi")
        yorum_cekilecek_yer = st.text_input("Lütfen analiz etmek istediğiniz yerin linkini giriniz:")
        maps_dosya_adi = st.text_input("Dosyanızı hangi isimle kayıt etmek istersiniz ?", key="dosya_kayit_adi")
        st.markdown("---")
        if st.button("Veri Çekimini Başlat", key="maps_analiz_buton",use_container_width=True, type="primary"):

            with st.spinner("Analiz Ediliyor"):
                # mapsDriverOlusturSC()
                # time.sleep(2)
                # mapsSoruCevapYuklemek()
                # driver.quit()

                mapsDriverOlustur()
                mapsDegerlendirmeYukleme()
                mapsYorumlariYuklemek()
                mapsPuanlariYuklemek()
                mapsYanitlariYuklemek()
                mapsIsimleriYuklemek()
                mapsTarihleriYuklemek()
                driver.quit()

                st.success(f"Çekim başarılı şekilde tamamlanmıştır, toplam çekilen değerlendirme sayısı:{len(maps_filtrelenmemis_degerlendirme_objeleri) }, Yorumlu değerlendirme sayısı: {len(maps_degerlendirme_objeleri)}")

                # simdi excel sablonu olusturayim 
                df_degerlendirmeler = pd.DataFrame({
                "İsim": maps_degerlendirme_isimleri,
                "Puan": maps_degerlendirme_puanlari,
                "Yorum": maps_degerlendirme_yorumlari,
                "Yanıt": maps_degerlendirme_yanitlari,
                "Tarih": maps_degerlendirme_tarihleri
                })

                df_soru_cevaplar = pd.DataFrame({
                "Soru": maps_sorular,
                "Cevap": maps_cevaplar
                })
                with pd.ExcelWriter(f"{maps_dosya_adi}.xlsx", engine="openpyxl") as writer:
                    df_degerlendirmeler.to_excel(writer, sheet_name="Değerlendirme", index=False)



streamlit_app()