#!/usr/bin/env python3
"""KW-02: official exported Android video handoff to Kwai, without posting."""
import hashlib, re, subprocess, sys, time, xml.etree.ElementTree as ET
from pathlib import Path

PKG="com.kwai.video"
ACTIVITY="com.kscorp.oversea.platform.router.ui.UriRouterActivity"
MEDIA=Path("/tmp/kw02-editor-entry-fixture.mp4")
NAME=None

def run(*argv,timeout=60):
    p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
    return p.returncode,p.stdout

def adb(*args,timeout=45):
    return run("adb",*args,timeout=timeout)

def ui():
    rc,_=adb("shell","uiautomator","dump","/sdcard/kw02-send-ui.xml",timeout=40)
    rc,out=adb("exec-out","cat","/sdcard/kw02-send-ui.xml",timeout=22)
    root=ET.fromstring(out)
    nodes=list(root.iter("node"))
    ids=" ".join((n.get("resource-id") or "").casefold() for n in nodes)
    labels=" ".join(((n.get("text") or "")+" "+(n.get("content-desc") or "")).casefold() for n in nodes)
    return ids,labels

def fg():
    _,out=adb("shell","dumpsys","activity","activities",timeout=30)
    return " ".join(line.strip() for line in out.splitlines() if "topResumedActivity" in line or "mResumedActivity" in line)[-500:]

def main():
    if not MEDIA.exists():
        rc,out=run("ffmpeg","-hide_banner","-loglevel","error","-nostdin","-y","-f","lavfi",
            "-i","color=c=black:s=320x240:r=24:d=2","-an","-c:v","libx264",
            "-pix_fmt","yuv420p","-movflags","+faststart",str(MEDIA),timeout=75)
        if rc or not MEDIA.exists() or MEDIA.stat().st_size<1000:
            print("KW02_SEND_MEDIA_GENERATION_FAILED")
            return 60
    size=MEDIA.stat().st_size
    digest=hashlib.sha256(MEDIA.read_bytes()).hexdigest()
    name="kw02-entry-"+digest[:12]+".mp4"
    remote="/sdcard/Movies/AntharesKw02/"+name
    adb("shell","mkdir","-p","/sdcard/Movies/AntharesKw02")
    rc,_=adb("push",str(MEDIA),remote,timeout=90)
    if rc:return 61
    adb("shell","am","broadcast","-a","android.intent.action.MEDIA_SCANNER_SCAN_FILE","-d","file://"+remote)
    time.sleep(4)
    _,listing=adb("shell","content","query","--uri","content://media/external/video/media",
                  "--projection","_id:_display_name:_size",timeout=35)
    rows=[line for line in listing.splitlines() if "_display_name="+name in line and "_size="+str(size) in line]
    if len(rows)!=1:
        print("KW02_SEND_MEDIASTORE_EXACT_MATCH="+str(len(rows)))
        return 62
    m=re.search(r"(?:^|[,\s])_id=(\d+)",rows[0])
    if not m:return 63
    uri="content://media/external/video/media/"+m.group(1)
    print("KW02_SEND_MEDIA_READY=YES")
    try:
        before_ids,before_labels=ui()
    except Exception:
        print("KW02_SEND_BASELINE_UNAVAILABLE")
        return 64
    rc,out=adb("shell","am","start","-W","-n",PKG+"/"+ACTIVITY,
               "-a","android.intent.action.SEND","-t","video/mp4",
               "-f","0x1","--eu","android.intent.extra.STREAM",uri,timeout=60)
    success=rc==0 and ("Status: ok" in out or "Complete" in out or "Starting:" in out)
    print("KW02_ACTION_SEND_ACTIVITY_LAUNCH="+("YES" if success else "NO"))
    if not success:return 65
    time.sleep(10)
    try:
        ids,labels=ui()
    except Exception:
        print("KW02_SEND_UI_UNAVAILABLE")
        return 66
    focus=fg().casefold()
    print("KW02_SEND_FOREGROUND_KWAI="+str(int(PKG in focus)))
    auth=any(x in ids for x in ("login_container","email_address_et","phone_number","signin","login_platform","verification_code")) or any(x in labels for x in ("continue with google","log in or sign up","enter phone number","verification code"))
    if auth:
        print("KW02_CREATE_REQUIRES_KW03_AUTH=YES")
        return 67
    if ids==before_ids and labels==before_labels:
        # Distinct official path: let Android select the exported Kwai SEND
        # handler rather than naming UriRouterActivity explicitly.
        rc2,out2=adb("shell","am","start","-W","-a","android.intent.action.SEND",
                   "-t","video/mp4","-p",PKG,"--grant-read-uri-permission",
                   "--eu","android.intent.extra.STREAM",uri,timeout=55)
        accepted=rc2==0 and ("Status: ok" in out2 or "Complete" in out2 or "Starting:" in out2)
        print("KW02_PACKAGE_RESOLVED_SEND_ACCEPTED="+str(int(accepted)))
        if accepted:
            time.sleep(12)
            ids,labels=ui()
            focus=fg().casefold()
            auth=any(x in ids for x in ("login_container","email_address_et","phone_number","signin","login_platform","verification_code")) or any(x in labels for x in ("continue with google","log in or sign up","enter phone number","verification code"))
            if auth:
                print("KW02_CREATE_REQUIRES_KW03_AUTH=YES")
                return 67
    editor_ids=("editor","video_edit","publish","caption","preview","video_trim","post","cover","photo_editor")
    editor_words=(" edit "," publish "," publicar "," trim "," legenda "," capa "," add music "," choose cover "," video editor "," select video ")
    editor=any(k in ids for k in editor_ids) or any(k in (" "+labels+" ") for k in editor_words)
    changed=ids!=before_ids or labels!=before_labels
    print("KW02_SEND_CHANGED_UI="+str(int(changed)))
    print("KW02_SEND_EDITOR_CONTROLS="+str(int(editor)))
    if PKG in focus and changed and editor:
        print("KW02_PUBLISH_INTERFACE_ACCESSIBLE=PASS")
        print("KW02_CREATE_ROUTE_CONFIRMED=EXPORTED_ACTION_SEND_VIDEO")
        return 0
    return 68

if __name__=="__main__":
    try:sys.exit(main())
    except Exception as exc:
        print("KW02_SEND_FAILED_CLASS="+type(exc).__name__)
        sys.exit(69)
