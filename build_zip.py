import json
import zipfile
import urllib.request
import re
from PIL import Image
from io import BytesIO

# Headers to prevent imgur from redirecting to the main site >:C
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MyImageFetcher/1.0)",
    "Accept": "image/avif,image/webp,image/png,image/*;q=0.8",
}

def build_zip():
    with open("z64games.json", encoding='utf-8-sig') as games_file:
        games = json.load(games_file)
        games = list(filter(lambda s: isinstance(s, dict), games))
        unsafeCharacters = r'[\\\/\.:*?"<>|]'

        # Pack all the game logos in a zip, for downloading purposes
        with zipfile.ZipFile("games.zip", 'a', zipfile.ZIP_DEFLATED) as binaries_zip:
            namelist_without_extensions = list(map(lambda x: x.split(".")[0], binaries_zip.namelist()))
            
            for i, entry in enumerate(games):
                try:
                    game = entry.get("game")
                    logo = entry.get("logo")
                    safe_game = re.sub(unsafeCharacters, "", game)

                    if safe_game in namelist_without_extensions: continue

                    print("- Packing logo for " + game)
                    if logo:
                        print("Downloading... " + logo)
                        request = urllib.request.Request(logo, headers=HEADERS)
                        with urllib.request.urlopen(request, timeout=30) as response:
                            format = response.headers.get("Content-Type", "").replace("image/", "")
                            logo_path = safe_game + ".png"
                            logo_data = response.read()

                            # If jpg, leave as is, since any compression will likely make it bigger
                            if format == "jpg" or format == "jpeg" or format == "avif":
                                logo_path = safe_game + "." + format
                                binaries_zip.writestr(logo_path, logo_data)

                            # Anything else convert to png and compress before saving
                            else:
                                image = Image.open(BytesIO(logo_data))
                                image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                                image = image.convert("RGBA").quantize(colors=256, method=Image.Quantize.FASTOCTREE)
                                output = BytesIO()
                                image.save(output, format="PNG", optimize=True, compress_level=9)
                                binaries_zip.writestr(logo_path, output.getvalue())

                            print("Packed " + logo_path)

                except Exception as e:
                    print(f"An error occured! {e}")
        return True


if __name__ == '__main__':
    print("BUILDING LOGOS ZIP")
    
    result = build_zip()

    if result: print("Process completed succesfully!")
    else: print("An error occured")