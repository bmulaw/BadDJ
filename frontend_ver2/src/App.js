import React, { Component } from 'react';
import { SpotifyAuth, Scopes } from 'react-spotify-auth'
import './App.css';
import Navbar from './components/Navbar';
import Profile from './components/pages/Profile';
import ShareMusic from './components/pages/ShareMusic';
import Feed from './components/pages/Feed';
import Notifications from './components/pages/Notifications';
import SignIn from './components/pages/SignIn';
import {BrowserRouter as Router, Switch, Route} from 'react-router-dom';
import { Helmet } from 'react-helmet'

const TITLE = "BADDJ"

class App extends Component {

    constructor() {
        super();
        this.state = { isAuthenticated: false, user: null, token: ''};
    }

    logout = () => {
        this.setState({isAuthenticated: false, token: '', user: null})
    };
    
    spotifyResponse = (e) => {};

    onFailure = (error) => {
      alert(error);
    }
    render() {
        let content = !!this.state.isAuthenticated ?
            (
                <div>
                    <p>Authenticated</p>
                    <div>
                        {this.state.user.email}
                    </div>
                    <div>
                        <button onClick={this.logout} className="button">
                            Log out
                        </button>
                    </div>
                </div>
            ) :
            (
                    <SpotifyAuth
                      redirectUri='http://localhost:8888/callback'
                      clientID='578597110fa642daaef83cd9c122d1d9'
                      scopes={[Scopes.userReadPrivate, Scopes.userReadEmail]}
                    />
            );
            

        return (
            <>
            <Helmet>
                <title>{ TITLE }</title>
            </Helmet>
            <Router>
              <Navbar />
                <Switch>
                  <Route path='/' exact/>
                  <Route path='/profile' component={Profile} />
                  <Route path='/share-music' component={ShareMusic} />
                  <Route path='/feed' component={Feed} />
                  <Route path='/notifications' component={Notifications} />
                  <Route path='/sign-in' component={SignIn} />
                </Switch>
            </Router>
            </>
          );
    }
}

export default App;