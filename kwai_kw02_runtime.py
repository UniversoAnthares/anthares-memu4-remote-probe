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
    if "isn\u0027t responding" in text or "is not responding" in text or "não está respondendo" in text:return "ANR"
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
    anr_attempts=0
    interest_attempts=0
    for i in range(38):
        nodes,text=screen()
        s=state(nodes,text)
        print("KW02_FSM_%02d=%s UI=%s"%(i,s,text[:350]),flush=True)
        if s=="MAIN":
            return nodes,text
        if s=="ANR":
            anr_attempts+=1
            print("KW02_ANR_RECOVERY=%d" % anr_attempts,flush=True)
            wants_close=("pixel launcher" in text and anr_attempts>=2) or ("kwai" in text and anr_attempts>=4)
            target="close app" if wants_close else "wait"
            n=rid(nodes,"aerr_close" if wants_close else "aerr_wait")
            if n is None:n=label(nodes,target,"fechar aplicativo" if wants_close else "aguardar")
            if n is not None:click(n)
            else:adb("shell","input","keyevent","4")
            time.sleep(8 if not wants_close else 4)
            if anr_attempts in (3,6):
                adb("shell","input","keyevent","3")
                time.sleep(3)
                relaunch()
            if anr_attempts>=9:raise RuntimeError("KW02_PERSISTENT_UI_ANR")
        elif s=="PERMISSION":
            n=rid(nodes,"permission_allow_button") or label(nodes,"allow","permitir")
            if n:click(n)
        elif s=="START":
            n=rid(nodes,"tiny_discovery_left_operation_btn") or label(nodes,"start now","continue","continuar")
            if n:click(n)
            else:adb("shell","input","swipe","850","1100","180","1100","250")
        elif s=="INTEREST_SELECT":
            interest_attempts+=1
            print("KW02_INTEREST_GATE_ATTEMPT=%d" % interest_attempts,flush=True)
            n=rid(nodes,"bt_interest_skip_top_right")
            if n is None:n=label(nodes,"skip","pular","skip for now")
            if interest_attempts<=2 and n is not None:
                click(n)
            elif interest_attempts==3:
                adb("shell","input","tap","90","250")
                time.sleep(2)
            else:
                choice=label(nodes,"comedy","music","gaming","dance","food")
                if choice is not None and interest_attempts in (4,6):
                    click(choice)
                proceed=label(nodes,"selected and continue","continue","next","continuar","avançar")
                if proceed is not None:
                    click(proceed)
                elif n is not None:click(n)
                else:adb("shell","input","keyevent","4")
            if interest_attempts==10:relaunch()
            if interest_attempts>=15:raise RuntimeError("KW02_INTEREST_ONBOARDING_BLOCKED")
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
    nodes,baseline=screen()
    sz=adb("shell","wm","size")
    m=re.search(r"(\d+)x(\d+)",sz)
    if not m:raise RuntimeError("KW02_DISPLAY_SIZE_UNKNOWN")
    width,height=map(int,m.groups())
    if not main_nav(nodes,baseline):raise RuntimeError("KW02_NATIVE_NAV_UNAVAILABLE")
    candidates=[]
    for n in nodes:
        ridx=n.get("resource-id","").casefold()
        lbl=(n.get("text","")+" "+n.get("content-desc","")).strip().casefold()
        p=ctr(n)
        if not p or p[1]<height*.73 or p[0]<width*.20 or p[0]>width*.80:continue
        if any(k in ridx for k in ("ll_camera","btn_camera","create","publish","record","shoot")) or lbl in ("+","create","criar","gravar"):
            candidates.append((p,"native:"+ridx[-90:]))
    candidates.append(((width//2,round(height*.955)),"nav-center"))
    candidates.append(((width//2,round(height*.92)),"nav-center-upper"))
    seen=set()
    for p,route in candidates:
        if p in seen:continue
        seen.add(p)
        print("KW02_CREATE_ATTEMPT=%s AT=%s"%(route,p),flush=True)
        adb("shell","input","tap",str(p[0]),str(p[1]))
        time.sleep(5)
        for i in range(4):
            nodes,text=screen()
            top=adb("shell","dumpsys","activity","activities")
            focus=" ".join(x.strip() for x in top.splitlines() if "topResumedActivity" in x or "mResumedActivity" in x or "mCurrentFocus" in x)[-500:]
            print("KW02_CREATE_UI=%s FOCUS=%s"%(text[:500],focus[:250]),flush=True)
            if resource_gate(text) or offline(text):
                time.sleep(4);continue
            permission=rid(nodes,"permission_allow_button")
            if permission is not None:
                click(permission);continue
            creator_labels=("album","gallery","upload","record","take photo","take picture","camera","câmera","choose video","select video","shoot","gravar","galeria","álbum","carregar","foto e vídeo")
            visual_creator=any(k in text for k in creator_labels)
            actual_activity=bool(re.search(r"(kwai|gifshow)[^\n]{0,160}(record|camera|capture|publish|editor|photopicker|album)",focus,re.I))
            changed=text!=baseline
            if changed and (visual_creator or actual_activity):
                print("KW02_PUBLISH_INTERFACE_ACCESSIBLE=PASS")
                print("KW02_CREATE_ROUTE_CONFIRMED="+route)
                return True
            login_wall=("continue with google" in text or "phone email" in text or "enter phone" in text or "verification code" in text or "sign up" in text) or (changed and not main_nav(nodes,text) and any(k in text for k in AUTH))
            if login_wall:
                print("KW02_CREATE_ROUTE_REQUIRES_KW03_AUTH=YES")
                return False
            if text==baseline:
                print("KW02_CREATE_UNCHANGED_FEED=YES")
                break
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
