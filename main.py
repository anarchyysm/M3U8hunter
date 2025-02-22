import requests
import json
from colorama import init, Fore, Style
import time
import random
import os
import logging  

# Configurando logging - mude o destino da pasta
logging.basicConfig(filename='/home/YOUR-USER/Documents/m3u8/script.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Inicializa o colorama
init()

def Logo():
    logo = r"""
{Fore.YELLOW}{Style.BRIGHT}
  __  __ ____  _    _  ___    _    _             _            
 |  \/  |___ \| |  | |/ _ \  | |  | |           | |           
 | \  / | __) | |  | | (_) | | |__| |_   _ _ __ | |_ ___ _ __ 
 | |\/| ||__ <| |  | |> _ <  |  __  | | | | '_ \| __/ _ \ '__|
 | |  | |___) | |__| | (_) | | |  | | |_| | | | | ||  __/ |   
 |_|  |_|____/ \____/ \___/  |_|  |_|\__,_|_| |_|\__\___|_|
                                               M3U8Hunter
{Style.RESET_ALL}
"""
    print(logo.format(Fore=Fore, Style=Style))

def get_video_url(video_id, max_retries=3):
    for attempt in range(max_retries):
        random_auth = str(random.randint(100000000, 999999999))
        
        headers = {
            "Host": "playback.video.globo.com",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "Referer": "https://globoplay.globo.com/",
            "Origin": "https://globoplay.globo.com",
            "Dnt": "1",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Authorization": random_auth,
            "Te": "trailers",
            "Cookie": "GBID=YOUR_GBID_COOKIE; GLBID=YOUR_GLBID_COOKIE; cookie-banner-consent-accepted=true",
            "Cookie-Banner-Accepted-Version": "1.4.2.4"
        }

        payload = {
            "player_type": "desktop",
            "video_id": video_id,
            "quality": "max",
            "content_protection": "widevine",
            "tz": "-03:00",
            "capabilities": {"low_latency": True},
            "consumption": "streaming",
            "metadata": {"name": "web", "device": {"type": "desktop", "os": {}}},
            "version": 1,
            "ts": 1740142090839
        }

        try:
            response = requests.post(
                "https://playback.video.globo.com/v4/video-session",
                headers=headers,
                json=payload,
                timeout=10
            )
            print(Fore.GREEN + Style.BRIGHT + "Fazendo requisição POST... " + Style.RESET_ALL)
            
            response.raise_for_status()
            print(Fore.GREEN + Style.BRIGHT + "Verificando se a requisição foi bem-sucedida... " + Style.RESET_ALL)
            
            data = response.json()
            print(Fore.GREEN + Style.BRIGHT + "Convertendo resposta pra JSON... " + Style.RESET_ALL)
            
            print(Fore.GREEN + Style.BRIGHT + "Extraindo a URL desejada: " + Style.RESET_ALL)
            for source in data.get("sources", []):
                if source.get("type") == "primary":
                    return source.get("url")
            return None
        except requests.exceptions.RequestException as e:
            error_msg = f"Tentativa {attempt+1}/{max_retries} falhou para {video_id}: {str(e)}"
            print(f"{Fore.RED}{Style.BRIGHT}{error_msg}{Style.RESET_ALL}")
            logging.error(error_msg)
            if attempt < max_retries - 1:
                time.sleep(5)  
            else:
                return None

# Mude o destino da pasta
def create_m3u8_file(filename, url, output_dir="/home/YOUR_USER/Documents/m3u8/"):
    os.makedirs(output_dir, exist_ok=True)
    
    m3u8_content = (
        "#EXTM3U\n"
        "#EXT-X-VERSION:3\n"
        '#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=4266656,CODECS="avc1.42c01e,mp4a.40.2",RESOLUTION=1920x1080\n'
        f"{url}\n"
    )
    
    filepath = os.path.join(output_dir, f"{filename}.m3u8")
    
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(m3u8_content)
    print(f"{Fore.GREEN}Arquivo {filepath} criado com sucesso!{Style.RESET_ALL}")
    logging.info(f"Arquivo {filepath} criado com sucesso")

if __name__ == "__main__":
    Logo()
    
    canais = {
        "6120663": "SinalAberto",
        "244881": "AcompanheCasa",
        "772202": "AcompanheCasa2",
        "10101606": "MosaicoBBB",
        "244887": "SegueLider",
        "772205": "QuartoAnos50",
        "6349747": "QuartoNordeste",
        "2254997": "QuartoFantastico",
        "244889": "Cozinha",
        "2254996": "CameraPantene",
        "2255000": "Sala",
        "244890": "Cozinha2",
        "2254993": "QuartoFantastico2"
    }

    for video_id, nome_arquivo in canais.items():
        print(f"\n{Fore.YELLOW}Processando {nome_arquivo} (video_id: {video_id}){Style.RESET_ALL}")
        video_url = get_video_url(video_id)
        
        if video_url:
            print(f"{Fore.WHITE}{Style.BRIGHT}URL obtida: {Style.RESET_ALL}{Fore.MAGENTA}{video_url}{Style.RESET_ALL}")
            create_m3u8_file(nome_arquivo, video_url)
        else:
            print(f"{Fore.RED}Não foi possível obter URL para {nome_arquivo}{Style.RESET_ALL}")
        
        time.sleep(15) 
