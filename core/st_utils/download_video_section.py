import os
import re
import shutil
import subprocess
from time import sleep
import threading

import streamlit as st
from core._1_ytdlp import download_video_ytdlp, download_video_async, find_video_files
from core.utils import *
from translations.translations import translate as t

OUTPUT_DIR = "output"

def download_video_section():
    st.header(t("a. Download or Upload Video"))
    
    # 初始化session state
    if 'download_started' not in st.session_state:
        st.session_state.download_started = False
    if 'high_quality_downloaded' not in st.session_state:
        st.session_state.high_quality_downloaded = False
    if 'low_quality_downloaded' not in st.session_state:
        st.session_state.low_quality_downloaded = False
    if 'download_thread' not in st.session_state:
        st.session_state.download_thread = None
    if 'auto_start_processing' not in st.session_state:
        st.session_state.auto_start_processing = False
    
    with st.container(border=True):
        try:
            # 检查是否有视频文件
            video_file = find_video_files()
            st.video(video_file)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(t("Delete and Reselect"), key="delete_video_button"):
                    os.remove(video_file)
                    if os.path.exists(OUTPUT_DIR):
                        shutil.rmtree(OUTPUT_DIR)
                    # 重置状态
                    st.session_state.download_started = False
                    st.session_state.high_quality_downloaded = False
                    st.session_state.low_quality_downloaded = False
                    st.session_state.download_thread = None
                    sleep(1)
                    st.rerun()
            
            with col2:
                if st.button(t("Start Processing Subtitles"), key="start_processing", type="primary"):
                    return "start_processing"
            
            with col3:
                # 添加烧录字幕按钮
                if os.path.exists("output/src_trans.ass") and st.button(t("Burn Subtitles"), key="burn_subtitles"):
                    return "burn_subtitles"
            
            # 显示下载状态
            if st.session_state.download_thread and st.session_state.download_thread.is_alive():
                st.info("⏳ 正在下载最高画质视频...")
            elif st.session_state.high_quality_downloaded:
                st.success("✅ 最高画质视频下载完成")
            
            return True
        except:
            # 下载区域
            url = st.text_input(t("Enter YouTube link:"))
            
            if st.button(t("Start Processing"), key="start_parallel_download", use_container_width=True, type="primary"):
                if url:
                    # 清理之前的文件
                    if os.path.exists(OUTPUT_DIR):
                        shutil.rmtree(OUTPUT_DIR)
                    os.makedirs(OUTPUT_DIR, exist_ok=True)
                    
                    # 先下载360p用于快速处理
                    with st.spinner("📥 正在下载360P视频用于快速处理..."):
                        download_video_ytdlp(url, resolution="360", suffix="_360p")
                        st.session_state.low_quality_downloaded = True
                    
                    # 异步下载最高画质
                    st.session_state.download_thread = download_video_async(url, resolution="best", suffix="_best")
                    st.session_state.download_started = True
                    st.session_state.high_quality_downloaded = False
                    
                    # 自动开始字幕处理
                    st.success("✅ 360P视频下载完成，开始自动字幕处理...")
                    st.session_state.auto_start_processing = True
                    sleep(2)
                    st.rerun()

            uploaded_file = st.file_uploader(t("Or upload video"), type=load_key("allowed_video_formats") + load_key("allowed_audio_formats"))
            if uploaded_file:
                if os.path.exists(OUTPUT_DIR):
                    shutil.rmtree(OUTPUT_DIR)
                os.makedirs(OUTPUT_DIR, exist_ok=True)
                
                raw_name = uploaded_file.name.replace(' ', '_')
                name, ext = os.path.splitext(raw_name)
                clean_name = re.sub(r'[^\w\-_\.]', '', name) + ext.lower()
                    
                with open(os.path.join(OUTPUT_DIR, clean_name), "wb") as f:
                    f.write(uploaded_file.getbuffer())

                if ext.lower() in load_key("allowed_audio_formats"):
                    convert_audio_to_video(os.path.join(OUTPUT_DIR, clean_name))
                
                # 上传完成后自动开始处理
                st.session_state.auto_start_processing = True
                st.rerun()
            else:
                return False

def convert_audio_to_video(audio_file: str) -> str:
    output_video = os.path.join(OUTPUT_DIR, 'black_screen.mp4')
    if not os.path.exists(output_video):
        print(f"🎵➡️🎬 Converting audio to video with FFmpeg ......")
        ffmpeg_cmd = ['ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=640x360', '-i', audio_file, '-shortest', '-c:v', 'libx264', '-c:a', 'aac', '-pix_fmt', 'yuv420p', output_video]
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True, encoding='utf-8')
        print(f"🎵➡️🎬 Converted <{audio_file}> to <{output_video}> with FFmpeg\n")
        # delete audio file
        os.remove(audio_file)
    return output_video
