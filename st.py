import streamlit as st
import os, sys
from core.st_utils.imports_and_utils import *
from core import *

# SET PATH
current_dir = os.path.dirname(os.path.abspath(__file__))
os.environ['PATH'] += os.pathsep + current_dir
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(page_title="VideoLingo", page_icon="docs/logo.svg")

SUB_VIDEO = "output/output_sub.mp4"
DUB_VIDEO = "output/output_dub.mp4"

def text_processing_section():
    st.header(t("b. Translate and Generate Subtitles"))
    with st.container(border=True):
        st.markdown(f"""
        <p style='font-size: 20px;'>
        {t("This stage includes the following steps:")}
        <p style='font-size: 20px;'>
            1. {t("WhisperX word-level transcription")}<br>
            2. {t("Sentence segmentation using NLP and LLM")}<br>
            3. {t("Summarization and multi-step translation")}<br>
            4. {t("Cutting and aligning long subtitles")}<br>
            5. {t("Generating timeline and subtitles")}<br>
            6. {t("Merging subtitles into the video")}
        """, unsafe_allow_html=True)

        if not os.path.exists(SUB_VIDEO):
            if st.button(t("Start Processing Subtitles"), key="text_processing_button"):
                process_text()
                st.rerun()
        else:
            if load_key("burn_subtitles"):
                st.video(SUB_VIDEO)
            download_subtitle_zip_button(text=t("Download All Srt Files"))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(t("Start Proofreading"), key="start_proofreading", type="primary"):
                    start_proofreading()
            with col2:
                if st.button(t("Open Output Folder"), key="open_output_folder_text"):
                    import subprocess
                    output_path = os.path.abspath("output")
                    subprocess.Popen(f'explorer "{output_path}"')
            with col3:
                if st.button(t("Archive to 'history'"), key="cleanup_in_text_processing"):
                    cleanup()
                    st.rerun()
            return True

def process_text():
    with st.spinner(t("Using Whisper for transcription...")):
        _2_asr.transcribe()
    with st.spinner(t("Splitting long sentences...")):  
        _3_1_split_nlp.split_by_spacy()
        _3_2_split_meaning.split_sentences_by_meaning()
    with st.spinner(t("Summarizing and translating...")):
        _4_1_summarize.get_summary()
        if load_key("pause_before_translate"):
            input(t("⚠️ PAUSE_BEFORE_TRANSLATE. Go to `output/log/terminology.json` to edit terminology. Then press ENTER to continue..."))
        _4_2_translate.translate_all()
    with st.spinner(t("Processing and aligning subtitles...")): 
        _5_split_sub.split_for_sub_main()
        _6_gen_sub.align_timestamp_main()
    with st.spinner(t("Merging subtitles to video...")):
        _7_sub_into_vid.merge_subtitles_to_video()
    
    st.success(t("Subtitle processing complete! 🎉"))
    st.balloons()

def audio_processing_section():
    st.header(t("c. Dubbing"))
    with st.container(border=True):
        st.markdown(f"""
        <p style='font-size: 20px;'>
        {t("This stage includes the following steps:")}
        <p style='font-size: 20px;'>
            1. {t("Generate audio tasks and chunks")}<br>
            2. {t("Extract reference audio")}<br>
            3. {t("Generate and merge audio files")}<br>
            4. {t("Merge final audio into video")}
        """, unsafe_allow_html=True)
        if not os.path.exists(DUB_VIDEO):
            if st.button(t("Start Audio Processing"), key="audio_processing_button"):
                process_audio()
                st.rerun()
        else:
            st.success(t("Audio processing is complete! You can check the audio files in the `output` folder."))
            if load_key("burn_subtitles"):
                st.video(DUB_VIDEO) 
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(t("Open Output Folder"), key="open_output_folder_audio"):
                    import subprocess
                    output_path = os.path.abspath("output")
                    subprocess.Popen(f'explorer "{output_path}"')
            with col2:
                if st.button(t("Delete dubbing files"), key="delete_dubbing_files"):
                    delete_dubbing_files()
                    st.rerun()
            with col3:
                if st.button(t("Archive to 'history'"), key="cleanup_in_audio_processing"):
                    cleanup()
                    st.rerun()

def process_audio():
    with st.spinner(t("Generate audio tasks")): 
        _8_1_audio_task.gen_audio_task_main()
        _8_2_dub_chunks.gen_dub_chunks()
    with st.spinner(t("Extract refer audio")):
        _9_refer_audio.extract_refer_audio_main()
    with st.spinner(t("Generate all audio")):
        _10_gen_audio.gen_audio()
    with st.spinner(t("Merge full audio")):
        _11_merge_audio.merge_full_audio()
    with st.spinner(t("Merge dubbing to the video")):
        _12_dub_to_vid.merge_video_audio()
    
    st.success(t("Audio processing complete! 🎇"))
    st.balloons()

def start_proofreading():
    """启动字幕校对工具"""
    import webbrowser
    import os
    
    # 检查必要的文件是否存在
    subtitle_file = "output/src_trans.ass"
    
    if not os.path.exists(subtitle_file):
        st.error("字幕文件 src_trans.ass 不存在，请先完成字幕生成步骤")
        return
    
    # 查找原始视频文件
    output_dir = "output"
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm']
    original_video = None
    
    for file in os.listdir(output_dir):
        if file.endswith(tuple(video_extensions)) and not file.startswith("output_"):
            original_video = os.path.join(output_dir, file)
            break
    
    if not original_video:
        st.error("未找到原始视频文件，请确保output目录中有视频文件")
        return
    
    st.success("✅ 字幕校对工具已启动！")
    st.info("正在打开字幕编辑器...")
    
    try:
        # 启动Streamlit字幕编辑器在8502端口
        import threading
        import time
        import subprocess
        
        def start_editor():
            # 启动字幕编辑器在8502端口
            subprocess.Popen(['streamlit', 'run', 'subtitle_editor_streamlit.py', '--server.port=8502'])
            time.sleep(2)  # 等待服务启动
            webbrowser.open_new_tab('http://localhost:8502')
        
        threading.Thread(target=start_editor, daemon=True).start()
        
        # 显示说明
        st.info("字幕编辑器将在新标签页中打开 (http://localhost:8502)")
        st.info("请在新打开的窗口中进行字幕校对")
        st.info("完成后关闭窗口即可返回主程序")
        
        # 提供手动启动的命令
        st.code("streamlit run subtitle_editor_streamlit.py --server.port=8502", language="bash")
        
    except Exception as e:
        st.error(f"启动字幕校对工具失败: {str(e)}")
        st.info("您可以手动运行以下命令:")
        st.code("streamlit run subtitle_editor_streamlit.py", language="bash")

def main():
    logo_col, _ = st.columns([1,1])
    with logo_col:
        st.image("docs/logo.png", use_column_width=True)
    st.markdown(button_style, unsafe_allow_html=True)
    welcome_text = t("Hello, welcome to VideoLingo. If you encounter any issues, feel free to get instant answers with our Free QA Agent <a href=\"https://share.fastgpt.in/chat/share?shareId=066w11n3r9aq6879r4z0v9rh\" target=\"_blank\">here</a>! You can also try out our SaaS website at <a href=\"https://videolingo.io\" target=\"_blank\">videolingo.io</a> for free!")
    st.markdown(f"<p style='font-size: 20px; color: #808080;'>{welcome_text}</p>", unsafe_allow_html=True)
    # add settings
    with st.sidebar:
        page_setting()
        st.markdown(give_star_button, unsafe_allow_html=True)
    download_video_section()
    text_processing_section()
    audio_processing_section()

if __name__ == "__main__":
    main()
