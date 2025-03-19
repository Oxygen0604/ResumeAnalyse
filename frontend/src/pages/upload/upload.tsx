import React, { useState,useRef, useEffect } from "react";
import "./upload.scss"
import Shell from "../../components/shell/shell.tsx";
import {useFileStore} from "../../store";

const Upload: React.FC = () => {
    interface File {
        id: number,
        data: any,
    }

    const uploadFile = useFileStore(state => state.uploadFile);
    const [file, setFile] = useState<File|null>(null);
    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        console.log(file);
        if (file) {
            uploadFile(file);
        }
    };

    return (
        <div className="upload">
            <div className="shell">
                <Shell />
            </div>

            <div className="upload-container">
                <div className="header">
                    <div className="title">
                        智聘通
                    </div>
                </div>

                <div className="content">
                    <div className="upload-box">
                        <div className="upload-form">
                            <div className="upload-title">
                                上传文件
                            </div>
                            <div className="upload-desc">
                                在下方上传想要分析的文件，我们将对其进行智能分析，并给出建议哦！
                            </div>
                            <form onSubmit={handleSubmit}>
                                <label htmlFor="file">
                                    <span>选择文件</span>
                                </label>
                                <input type="file" id="file" name="file" multiple={false} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFile(e.target.files?{id:0,data:e.target.files[0]}:null)}/>
                                <button type="submit">开始分析</button>
                            </form>
                        </div>

                        <div className="upload-result">
                            <div className="result-title">
                                已上传文件
                            </div>
                            <div className="result">
                                {file?.data?.name ?? ""}
                            </div>
                        </div>
                    </div>
                    
                </div>

                <div className="footer">

                </div>
            </div>
        </div>
    );
}   

export default Upload;