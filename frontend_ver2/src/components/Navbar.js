import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import 'react-spotify-auth/dist/index.css'
import './Navbar.css';
import { SpotifyAuth, Scopes } from 'react-spotify-auth';

function Navbar() {
    const [click, setClick] = useState(false);
    const [button, setButton] = useState(true);

    const handleClick = () => setClick(!click);
    const closeMobileMenu = () => setClick(false);

    const showButton = () => {
        if(window.innerWidth <= 960) {
            setButton(false);
        } else {
            setButton(true);
        }
    };

    useEffect(() => {
        showButton()
    }, []);

    window.addEventListener('resize', showButton);

    return (
       <>
        <nav className='navbar'>
            <div className='navbar-container'>
                <Link to='/' className='navbar-logo' onClick={closeMobileMenu}>
                    BADDJ
                </Link>
                <div className='menu-icon' onClick={handleClick}>
                    <i className={click ? 'fas fa-times' : 'fas fa-bars'} />
                </div>
                <ul className={click ? 'nav-menu active' : 'nav-menu'}>
                    <li className='nav-item'>
                        <Link to='/' className='nav-links' onClick={closeMobileMenu}>
                        &nbsp;&nbsp;Discover&nbsp;&nbsp;
                        </Link>
                    </li>
                    <li className='nav-item'>
                        <Link to='/share-music' className='nav-links' onClick={closeMobileMenu}>
                            Share&ensp;Music
                        </Link>
                    </li>
                    <li className='nav-item'>
                        <Link to='/profile' className='nav-links' onClick={closeMobileMenu}>
                        &nbsp;&nbsp;&nbsp;Profile&nbsp;&nbsp;&nbsp;
                        </Link>
                    </li>
                    <li className='nav-item'>
                        <Link to='/notifications' className='nav-links' onClick={closeMobileMenu}>
                            Notifications
                        </Link>
                    </li>
                    <li className='nav-item'>
                        <SpotifyAuth
                            redirectUri='http://localhost:3000/callback'
                            clientID=""
                            scopes={[Scopes.userReadPrivate, Scopes.userReadEmail]}
                        /> 
                    </li>
                </ul>
                {/* {button && <Button buttonStyle='btn--outline'>SIGN UP</Button>} */}
            </div>
        </nav>
       </>
    );
}

export default Navbar;
