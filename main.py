#SAPI4 Klein process

import quart,subprocess,zlib,asyncio,hashlib,subprocess,os,shlex,time
from quart import Response

app = quart.Quart(__name__)

async def gen_sapi4(text,speed,pitch,voice,ident):
    name = hashlib.md5(f'{text}{speed}{pitch}{voice}{ident}'.encode()).hexdigest()
    infile = "./" + name + '.wav'
    outfile = os.path.join("./tmp_audio", name + '.mp3')
    tries = 0
    while tries < 10:
        tries += 1
        if not os.path.exists(infile):
            command = f'xvfb-run -a -n 10 wine ./sapi4.exe -v "{voice}" -s {speed} -p {pitch} -t "{text}" -o "{infile}"'
            x = await asyncio.create_subprocess_shell(command)
            await x.wait()
    if os.path.exists(infile):
        y = await convert(infile,outfile)
        os.remove(infile)
        return y
    else:
        return None

async def gen_dectalk(text,ident):

    name = hashlib.md5(f'{text}{ident}'.encode()).hexdigest()
    infile = "./" + name + '.wav'
    outfile = os.path.join("./tmp_audio", name + '.mp3')
    tries = 0
    while tries < 10:
        tries += 1
        if not os.path.exists(infile):    
            command = f'xvfb-run -a -n 10 wine ./say.exe -w "{infile}" "{text}"'
            x = await asyncio.create_subprocess_shell(command)
            await x.wait()
    if os.path.exists(infile):
        y = await convert(infile,outfile)
        os.remove(infile)
        return y
    else:
        return None

async def convert(infile,outfile):
    ffmpeg_cmd = f'ffmpeg -y -i "{infile}" -codec:a libmp3lame -q:a 9 -ac 1 "{outfile}"'
    tries = 0
    while tries < 10:
        tries += 1
        if not os.path.exists(outfile):
            x = await asyncio.create_subprocess_shell(ffmpeg_cmd)
            await x.wait()
    if os.path.exists(outfile):
        return outfile
    else:
        return None

@app.route("/sapi4")
async def sapi4():
    bonzi = quart.request.args.get("bonzi")
    text = quart.request.args.get("text")
    if not bonzi:
        voice = quart.request.args.get("voice")
        speed = quart.request.args.get("speed")
        pitch = quart.request.args.get("pitch")
        zipped = quart.request.args.get("zipped")
        if not voice: voice = "Adult Male #2, American English (TruVoice)"
        if not speed: speed = 120
        if not pitch: pitch = 100
    else:
        voice = "Adult Male #2, American English (TruVoice)"
        pitch = 140
        speed = 157
    if not text: return Response("Server Error",status=500)
    ident = quart.request.args.get("id")
    filename = await gen_sapi4(text,speed,pitch,voice,ident)
    if filename:
        return await quart.send_file(filename)
    else:
        return Response("Server Error",status=500)
    
@app.route("/dectalk")
async def dectalk():
    text = quart.request.args.get("text")
    ident = quart.request.args.get("id")
    filename = await gen_dectalk(text,ident)
    if filename:
        return await quart.send_file(filename)
    else:
        return Response("Server Error",status=500)
    
@app.route("/rehost")
async def rehost():
    filename = quart.request.args.get("filename")
    
    if filename:
        filename = os.path.join("./tmp_audio",filename)
        return await quart.send_file(filename)
    else:
        return Response("Server Error",status=500)
    
if not os.path.exists("./tmp_audio"):
    os.makedirs("./tmp_audio")

file_to_install = ['msttsl.exe','spchapi.exe','tv_enua.exe','lhttsged.exe']    
for file in file_to_install:
    y = os.path.join('.','installers',file)
    process = subprocess.Popen(shlex.split(f'xvfb-run -a -n 10 wine {y} /Q'))
    process.wait(30)
    
app.run(host="0.0.0.0", port=9999)