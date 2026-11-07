#!/usr/bin/env python3
"""KW-02: advance official Kwai Android UI, recover network gate, open creator.
No credentials, posts, media or persistent profile touched.
"""
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

PKG="com.kwai.video"
OFFLINE=("can't connect to server","cannot connect to server","no internet","sem internet","sem conexão","sem conexao","network unavailable","internet's a bit slow")
LOADING=("resource downloading","hang in there","skip the preparation","download failed")
COMPOSER=("upload","album","gallery","record","shoot","shooting","capturar","gravar","camera","câmera","create a video","create video","select video","select photos","choose from album","permission to access","allow kwai to take","photos and videos")
AUTH=("please log in","log in","sign in","login","entrar","cadastre-se","phone number","email address","verification code")

def adb(*args,timeout=22):
    x=subprocess.run(["adb",*args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
    return x.stdout

def screen():
    adb("shell","uiautomator","dump","/sdcard/kw02-ui.xml",timeout=45)
    xml=adb("exec-out","cat","/sdcard/kw02-ui.xml",timeout=15)
    root=ET.fromstring(xml)
    nodes=list(root.iter("node"))
    labels=[(n.get("text","")+" "+n.get("content-desc","")).strip().casefold() for n in nodes]
    return nodes," ".join(t for t in labels if t)

def ctr(n):
    m=re.fullmatch(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]",n.get("bounds",""))
    if not m:return None
    a,b,c,d=map(int,m.groups())
    return ((a+c)//2,(b+d)//2)

def click(n):
    p=ctr(n)
    if not p:return False
    adb("shell","input","tap",str(p[0]),str(p[1]))
    time.sleep(2)
    return True

def rid(nodes,*suffixes):
    for suffix in suffixes:
        for n in nodes:
            if n.get("resource-id","").endswith(suffix) and ctr(n):
                return n
    return None

def label(nodes,*values):
    for n in nodes:
        v=(n.get("text","")+" "+n.get("content-desc","")).strip().casefold()
        if v in values and ctr(n):return n
    return None

def main_nav(nodes,text):
    count=sum(w in text for w in ("home","discover","inbox","profile","following","inicio","início","perfil","mensagens"))
    return count>=3 or (rid(nodes,"ll_profile") is not None and count>=2)

def resource_gate(text):
    return any(x in text for x in LOADING)

def offline(text):
    return any(x in text for x in OFFLINE)

def state(nodes,text):
    if main_nav(nodes,text):return "MAIN"
    if resource_gate(text):return "RESOURCE"
    if "start now" in text or "you're all set" in text or "you’re all set" in text:return "START"
    if "select your interests" in text:return "INTEREST_SELECT"
    if "choose like or dislike" in text:return "INTEREST"
    if "permissioncontroller" in " ".join(n.get("resource-id","").casefold() for n in nodes):return "PERMISSION"
    return "OTHER"

def relaunch():
    adb("shell","am","force-stop",PKG)
    time.sleep(2)
    adb("shell","monkey","-p",PKG,"-c","android.intent.category.LAUNCHER","1")
    time.sleep(8)

def recover_network():
    print("KW02_NETWORK_RECOVERY=WIFI_RECONNECT")
    adb("shell","svc","wifi","disable")
    time.sleep(2)
    adb("shell","svc","wifi","enable")
    time.sleep(8)
    relaunch()

def navigate():
    adb("shell","pm","grant",PKG,"android.permission.POST_NOTIFICATIONS")
    recovery_count=0
    resource_attempts=0
    for i in range(38):
        nodes,text=screen()
        s=state(nodes,text)
        print("KW02_FSM_%02d=%s UI=%s"%(i,s,text[:350]),flush=True)
        if s=="MAIN":
            return nodes,text
        if s=="PERMISSION":
            n=rid(nodes,"permission_allow_button") or label(nodes,"allow","permitir")
            if n:click(n)
        elif s=="START":
            n=rid(nodes,"tiny_discovery_left_operation_btn") or label(nodes,"start now","continue","continuar")
            if n:click(n)
            else:adb("shell","input","swipe","850","1100","180","1100","250")
        elif s=="INTEREST_SELECT":
            n=label(nodes,"skip","pular","skip for now")
            if n:click(n)
            else:adb("shell","input","tap","90","250")
        elif s=="INTEREST":
            n=rid(nodes,"tiny_discovery_dislike_button","tiny_discovery_like_button")
            if n:click(n)
            else:adb("shell","input","swipe","850","1100","180","1100","250")
        elif s=="RESOURCE":
            resource_attempts+=1
            n=label(nodes,"yes, skip","skip","cancel","skip the preparation","pular")
            if n:click(n)
            else:
                n=rid(nodes,"btn_cancel")
                if n:click(n)
                else:time.sleep(7)
            if resource_attempts in (5,9):
                if recovery_count<1:
                    recover_network();recovery_count+=1
                else:relaunch()
        else:
            n=label(nodes,"next","continue","skip","start now","got it","ok")
            if n:click(n)
            elif i%4==3 and i>3:relaunch()
            else:adb("shell","input","swipe","850","1100","180","1100","250")
        time.sleep(3)
    raise RuntimeError("KW02_MAIN_NAV_NOT_REACHED")

def stabilized():
    for i in range(5):
        nodes,text=screen()
        print("KW02_NETWORK_CHECK_%d=%s"%(i,text[:430]),flush=True)
        if not main_nav(nodes,text):
            if i<4:time.sleep(5);continue
            raise RuntimeError("KW02_NAV_DISAPPEARED")
        if resource_gate(text) or offline(text):
            if i<3:
                time.sleep(5);continue
            raise RuntimeError("KW02_NETWORK_OR_RESOURCES_STILL_BLOCKED")
        time.sleep(4)
    print("KW02_REAL_FEED_NAVIGATION=PASS")
    print("KW02_NETWORK_AND_RESOURCE_GATE=PASS")
    return nodes,text

def creator():
    nodes,text=screen()
    # Native create control sometimes has an unlabeled '+' in the bottom navigation.
    selected=None
    for n in nodes:
        ridx=n.get("resource-id","").casefold()
        lbl=(n.get("text","")+" "+n.get("content-desc","")).strip().casefold()
        p=ctr(n)
        if not p:continue
        if any(k in ridx for k in ("ll_camera","btn_camera","create","publish","record")) or lbl in ("+","create","criar","gravar"):
            selected=n;break
    if selected:
        print("KW02_CREATE_ROUTE=SEMANTIC_NATIVE")
        click(selected)
    elif main_nav(nodes,text):
        size=adb("shell","wm","size")
        m=re.search(r"(\d+)x(\d+)",size)
        if not m:raise RuntimeError("KW02_DISPLAY_SIZE_UNKNOWN")
        w,h=map(int,m.groups())
        adb("shell","input","tap",str(w//2),str(round(h*.95)))
        print("KW02_CREATE_ROUTE=MAIN_NAV_CENTER")
        time.sleep(5)
    else:raise RuntimeError("KW02_NATIVE_NAV_UNAVAILABLE")
    for i in range(8):
        nodes,text=screen()
        fg=adb("shell","dumpsys","window").casefold()[-1700:]
        print("KW02_COMPOSER_CHECK_%d=%s"%(i,text[:440]),flush=True)
        if resource_gate(text) or offline(text):
            if i>=5:raise RuntimeError("KW02_CREATE_NETWORK_BLOCKED")
            time.sleep(3);continue
        permission=rid(nodes,"permission_allow_button")
        if permission:
            click(permission);continue
        if any(k in text for k in COMPOSER) or any(k in fg for k in ("capture","recordactivity","cameraactivity","publishactivity","photopicker","permissioncontroller")):
            print("KW02_PUBLISH_INTERFACE_ACCESSIBLE=PASS")
            return True
        if any(k in text for k in AUTH):
            print("KW02_CREATE_ROUTE_REQUIRES_KW03_AUTH=YES")
            return False
        time.sleep(3)
    raise RuntimeError("KW02_COMPOSER_NOT_REACHED")

def run():
    assert adb("shell","getprop","sys.boot_completed").strip()=="1"
    packages=adb("shell","pm","path",PKG)
    assert "package:" in packages
    print("KW02_OFFICIAL_KWAI_INSTALLED=YES")
    adb("shell","monkey","-p",PKG,"-c","android.intent.category.LAUNCHER","1")
    time.sleep(12)
    navigate()
    stabilized()
    if not creator():
        raise RuntimeError("KW02_PUBLICATION_UI_BLOCKED_BY_AUTH_KW03")
    print("KW02_COMPLETE=PASS")

if __name__=="__main__":
    try:run()
    except Exception as exc:
        print("KW02_FAILED="+str(exc))
        sys.exit(30)
