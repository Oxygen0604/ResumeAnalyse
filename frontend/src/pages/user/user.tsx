import React from'react';
import "./user.scss";
import Shell from '../../components/shell/shell';
import { useAuthStore } from '../../store';

const User = () => {
  const logout = useAuthStore(state => state.logout);

  const handleOnClick = () => {
    logout();
    window.location.href = '/';
  }
  return (
    <div className="user">
      <div className='shell'>
        <Shell />
      </div>

      <div className='user-content'>
        <div className='user-header'>

        </div>

        <div className='user-body'>
          <button onClick={handleOnClick}>登出</button>
        </div>

        <div className='user-footer'>

        </div>
      </div>
    </div>
    );
}

export default User;