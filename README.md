Veri çekme ve analiz uygulaması

Amaç:
Bu uygulama, e-ticaret sitelerindeki ürünlerin  verilerini çekip yapay zeka ile analiz ederek Excel formatında raporlar oluşturmayı amaçlamaktadır.


Kurulum ve Gerekli Kütüphaneler
Projeyi çalıştırmadan önce aşağıdaki Python kütüphanelerinin yüklü olması gerekmektedir.
terminale bu satırı giriniz: pip install streamlit selenium beautifulsoup4 pandas openai tiktoken google-generativeai


ChromeDriver Kurulumu
Uygulamanın çalışabilmesi için sisteminizde ChromeDriver kurulu olmalıdır. Kurulum adımları:
https://googlechromelabs.github.io/chrome-for-testing adresine gidin.
Stable sürümünün altında işletim sisteminize uygun versiyonu indirin.
Çıkan klasör içinde chromedriver dosyasını alın ve sisteminizde bir klasöre taşıyın (örneğin: /Users/kullanici_adi/Drivers/).
Uygulamadaki chrome_driver_path değişkeni, bu dosyanın tam yolunu göstermelidir. Örnek:chrome_driver_path = "/Users/erenates/Drivers/chromedriver"
