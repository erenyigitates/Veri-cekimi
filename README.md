Veri çekme ve analiz uygulaması

Amaç:
Bu uygulama, e-ticaret sitesindeki ve google haritalardaki verileri çekip yapay zeka ile analiz ederek Excel formatında raporlar oluşturmayı amaçlamaktadır.


Kurulum ve Gerekli Kütüphaneler
Projeyi çalıştırmadan önce aşağıdaki Python kütüphanelerinin yüklü olması gerekmektedir.
terminale bu satırı giriniz: pip install streamlit selenium beautifulsoup4 pandas openai tiktoken google-generativeai


ChromeDriver Kurulumu
Uygulamanın çalışabilmesi için sisteminizde ChromeDriver kurulu olmalıdır. Kurulum adımları:
https://googlechromelabs.github.io/chrome-for-testing adresine gidin.
Stable sürümünün altındaki chromedriver lardan işletim sisteminize uygun versiyonu indirin.
Çıkan klasör içinde chromedriver dosyasını alın ve sisteminizde bir klasöre taşıyın (örneğin: /Users/kullanici_adi/Drivers/).

Koddaki chrome_driver_path değişkeni, bu dosyanın tam yolunu göstermelidir. 
MACOS Örneği : chrome_driver_path = "/Users/erenates/Drivers/chromedriver"
WINDOWS Örneği : chrome_driver_path = r"C:\Users\erenates\Drivers\chromedriver.exe"


Önemli Uyarı – ChromeDriver Güncelliği
ChromeDriver sürümünüz, yüklü olan Google Chrome tarayıcınızla uyumlu olmalıdır. Aksi takdirde uygulama çalışmayabilir veya selenium hata verebilir.
Google Chrome tarayıcınızı güncellediğinizde, ChromeDriver'ı da mutlaka güncellemeniz gerekir.
En güncel sürümleri ve tarayıcınıza uygun versiyonu buradan kontrol edebilirsiniz:
https://googlechromelabs.github.io/chrome-for-testing

Kod dosyanız ile logo.jpg görseli aynı klasörde bulunmalıdır.

Aksi takdirde uygulama, logoyu yükleyemez ve hata verebilir.

Veri anailz sekmesinde yukleyeceginiz excel tablosunun icinde "yorum" baslikli sutun olmasi yeterlidir
