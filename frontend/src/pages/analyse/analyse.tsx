import React, { useState, useEffect } from'react';
import "./analyse.scss";
import Shell from '../../components/shell/shell';

const Analyse: React.FC = () => {
    return(
        <div className="analyse">
            <div className='shell'>
                <Shell />
            </div>

            <div className='container'>
                <div className='header'>
                    <div className='title'>
                        分析结果
                    </div>
                </div>

                <div className='content'>

                </div>
            
                <div className='footer'>

                </div>
            </div>
            
        </div>
    )
}

export default Analyse;