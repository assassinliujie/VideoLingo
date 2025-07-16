import streamlit as st
import os, sys
from core.st_utils.imports_and_utils import *
from core import *
from core.subtitle_burner import burn_subtitle_to_video

# SET PATH
current_dir = os.path.dirname(os.path.abspath(__file__))
os.environ['PATH'] += os.pathsep + current_dir
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(page_title="Alizoed's翻译工具", page_icon="docs/logo.svg")

SUB_VIDEO = "output/output_sub.mp4"
DUB_VIDEO = "output/output_dub.mp4"

def text_processing_section():
    # 处理自动处理的加载状态
    if st.session_state.get('auto_processing_in_progress', False):
        with st.spinner("🔄 AI正在处理字幕..."):
            return True

    if not os.path.exists(SUB_VIDEO):
        # 如果没有处理过，显示开始按钮
        if not st.session_state.get('auto_processing_completed', False):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 开始AI字幕处理", key="text_processing_button", use_container_width=True, type="primary"):
                    process_text()
                    st.rerun()
    else:
        # 已有处理结果，显示操作按钮
        if load_key("burn_subtitles"):
            st.video(SUB_VIDEO)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✏️ 字幕校对", key="start_proofreading", type="primary"):
                start_proofreading()
        with col2:
            if st.button("📁 打开文件夹", key="open_output_folder_text"):
                import subprocess
                output_path = os.path.abspath("output")
                subprocess.Popen(f'explorer "{output_path}"')
        with col3:
            download_subtitle_zip_button(text="📥 下载字幕包")
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
        # 直接调用，让ffmpeg在终端显示输出
        _7_sub_into_vid.merge_subtitles_to_video()
    
    st.success(t("Subtitle processing complete! 🎉"))
    st.balloons()

def audio_processing_section():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 20px; border-radius: 15px; margin: 20px 0;'>
        <h3 style='color: white; margin: 0; font-size: 1.5em;'>
            🔊 第三步：AI智能配音
        </h3>
        <p style='color: rgba(255,255,255,0.9); margin: 10px 0 0 0;'>
            语音合成与视频完美融合
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div style='background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 5px solid #fa709a;'>
            <h4 style='color: #333; margin-top: 0;'>🎵 配音流程</h4>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-top: 15px;'>
                <div style='background: #fff5f5; padding: 15px; border-radius: 10px; border-left: 3px solid #fa709a;'>
                    <strong>🎯 任务生成</strong><br>
                    <small>智能音频分段</small>
                </div>
                <div style='background: #fff5f5; padding: 15px; border-radius: 10px; border-left: 3px solid #fa709a;'>
                    <strong>🗣️ 语音克隆</strong><br>
                    <small>AI语音合成</small>
                </div>
                <div style='background: #fff5f5; padding: 15px; border-radius: 10px; border-left: 3px solid #fa709a;'>
                    <strong>🎚️ 音频合并</strong><br>
                    <small>无缝音频整合</small>
                </div>
                <div style='background: #fff5f5; padding: 15px; border-radius: 10px; border-left: 3px solid #fa709a;'>
                    <strong>🎬 视频合成</strong><br>
                    <small>最终视频输出</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if not os.path.exists(DUB_VIDEO):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🎙️ 开始AI配音", key="audio_processing_button", use_container_width=True, type="primary"):
                    process_audio()
                    st.rerun()
        else:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 15px; margin: 20px 0; color: white; text-align: center;'>
                <h4 style='margin: 0;'>🎉 配音完成！</h4>
                <p style='margin: 5px 0 0 0; opacity: 0.9;'>AI配音已完美同步到视频</p>
            </div>
            """, unsafe_allow_html=True)
            if load_key("burn_subtitles"):
                st.video(DUB_VIDEO) 
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📁 打开文件夹", key="open_output_folder_audio", use_container_width=True):
                    import subprocess
                    output_path = os.path.abspath("output")
                    subprocess.Popen(f'explorer "{output_path}"')
            with col2:
                if st.button("🗑️ 删除配音", key="delete_dubbing_files", use_container_width=True):
                    delete_dubbing_files()
                    st.rerun()
            with col3:
                if st.button("🗂️ 清理文件", key="cleanup_in_audio_processing", use_container_width=True):
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
    from core.subtitle_burner import get_highest_quality_video
    
    # 检查必要的文件是否存在
    subtitle_file = "output/src_trans.ass"
    
    if not os.path.exists(subtitle_file):
        st.error("字幕文件 src_trans.ass 不存在，请先完成字幕生成步骤")
        return
    
    # 查找最高质量视频文件
    original_video = get_highest_quality_video()
    
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
    st.markdown("""
    <style>
    /* 全局样式变量 */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --success-gradient: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        --warning-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --info-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        --background: #f8fafc;
        --surface: #ffffff;
        --text-primary: #1a202c;
        --text-secondary: #718096;
        --border: #e2e8f0;
        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* 响应式网格布局 */
    .responsive-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin: 1rem 0;
    }
    
    @media (max-width: 768px) {
        .responsive-grid {
            grid-template-columns: 1fr;
            gap: 1rem;
        }
    }
    
    /* 卡片样式 */
    .feature-card {
        background: var(--surface);
        border-radius: 15px;
        box-shadow: var(--shadow);
        border: 1px solid var(--border);
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }
    
    /* 标题样式 */
    .main-title {
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3em;
        font-weight: 700;
        text-align: center;
        margin: 0.5em 0;
    }
    
    .subtitle {
        color: var(--text-secondary);
        font-size: 1.3em;
        text-align: center;
        margin-bottom: 2em;
    }
    
    /* 响应式按钮 */
    .responsive-button {
        width: 100%;
        max-width: 300px;
        margin: 0 auto;
    }
    
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5em;
        }
        
        .subtitle {
            font-size: 1.1em;
        }
    }
    
    @media (max-width: 480px) {
        .main-title {
            font-size: 2em;
        }
        
        .subtitle {
            font-size: 1em;
        }
    }
    </style>
    <div class='main-title'>Alizoed's翻译工具</div>
    <p class='subtitle'>AI驱动的视频翻译与配音工具</p>
    """, unsafe_allow_html=True)
    
    # 初始化自动处理状态
    if 'auto_processing_in_progress' not in st.session_state:
        st.session_state.auto_processing_in_progress = False
    if 'auto_processing_completed' not in st.session_state:
        st.session_state.auto_processing_completed = False
    
    # 处理烧录字幕的请求
    if 'burn_subtitles' in st.session_state and st.session_state.burn_subtitles:
        try:
            with st.spinner("🔥 正在烧录字幕到视频中..."):
                output_file = burn_subtitle_to_video()
                st.success(f"✅ 字幕烧录完成！文件已保存为: {output_file}")
                st.video(output_file)
                st.session_state.burn_subtitles = False
        except Exception as e:
            st.error(f"❌ 字幕烧录失败: {str(e)}")
            st.session_state.burn_subtitles = False
    
    # 设置信息已移至配置文件，不再显示侧边栏
    
    # 处理下载部分的返回
    download_result = download_video_section()
    
    # 处理自动字幕处理
    if st.session_state.get('auto_start_processing', False):
        st.session_state.auto_start_processing = False
        st.session_state.auto_processing_in_progress = True
        
        try:
            process_text()
            st.session_state.auto_processing_completed = True
        finally:
            st.session_state.auto_processing_in_progress = False
        st.rerun()
    
    if download_result == "start_processing":
        # 开始字幕处理（备用路径）
        process_text()
        st.rerun()
    elif download_result == "burn_subtitles":
        # 设置烧录字幕标志
        st.session_state.burn_subtitles = True
        st.rerun()
    
    text_processing_section()
    audio_processing_section()

if __name__ == "__main__":
    main()
