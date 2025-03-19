import React from'react';
import "./home.scss";
import Shell from '../../components/shell/shell';

const Home = () => {
  return (
    <div className="home">

        <div className='shell'>
            <Shell />
        </div>

        <div className='header'>

        </div>

        <div className='content'>
            <div className='title'>
              Welcome
            </div>
            <div className='text'>
              <div>
                欢迎来到我们的平台！
              </div>
              <div>
                平台支持对上传的简历进行结构化解析，自动提取包括个人信息、教育背景、工作经历、技能特长、职业意向等在内的关键信息。通过智能分析引擎，生成个性化的简历报告。
              </div>
            </div>
        </div>

        <div className='footer'>

        </div>
    </div>
  );
}

export default Home;