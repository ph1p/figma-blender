import { observer } from 'mobx-react-lite';
import React, { FunctionComponent } from 'react';
import styled, { keyframes } from 'styled-components';
import { BlenderLogo } from '../assets/BlenderLogo';
import { ElementIcon } from '../assets/ElementIcon';
import { FigmaLogo } from '../assets/FigmaLogo';
import { PageIcon } from '../assets/PageIcon';
import EventEmitter from '../shared/EventEmitter';

import { useStore } from '../store';
import { ConnectionEnum } from '../utils/interfaces';

const FooterElement = () => (
  <Footer>
    <a href="https://ph1p.gumroad.com/l/figma-blender-addon" target="_blank">
      Get the Blender Addon (it's free) {'->'}
    </a>
  </Footer>
);

const Home: FunctionComponent = observer(() => {
  const store = useStore();

  const askForFrames = () => EventEmitter.emit('get elements');

  if (store.status === ConnectionEnum.CONNECTING || store.notAllowed) {
    return (
      <Wrapper>
        <Loader>
          <p>
            {store.notAllowed ? (
              <>
                One connected plugin
                <br />
                at a time is allowed
              </>
            ) : (
              'Waiting for Blender...'
            )}
          </p>
          <Progress></Progress>
        </Loader>
        <FooterElement />
      </Wrapper>
    );
  }

  return (
    <Wrapper>
      <div>
        <List>
          <li>
            <div className="name">
              <ElementIcon className="icon element" />
              Elements
            </div>
            <div>{store.elements.length}</div>
          </li>
          <li>
            <div className="name">
              <PageIcon className="icon" />
              Page
            </div>
            <div>{store.page_name}</div>
          </li>
        </List>
        <Button onClick={askForFrames}>
          <div className="icon">
            <FigmaLogo />
          </div>
          <div>Update Elements</div>
          <div className="icon">
            <BlenderLogo />
          </div>
        </Button>
      </div>

      <FooterElement />
    </Wrapper>
  );
});

const List = styled.ul`
  list-style: none;
  margin: 0 0 12px;
  padding: 0;
  li {
    font-weight: 600;
    background-color: var(--figma-color-bg);
    display: flex;
    padding: 12px 15px;
    border-radius: 8px 8px 0 0;
    justify-content: space-between;
    div {
      align-self: center;
      align-items: center;
    }
    .name {
      display: flex;
      .icon {
        margin-right: 12px;
        &.element {
          width: 12px;
          height: 12px;
        }
        path {
          fill: var(--figma-color-text);
        }
      }
    }
    &:last-child {
      margin-top: 1px;
      border-radius: 0 0 8px 8px;
    }
  }
`;

const Footer = styled.footer`
  font-size: 11px;
  color: #888888;
  text-align: center;
  a {
    color: #888888;
  }
`;

const Wrapper = styled.div`
  display: grid;
  grid-template-rows: 1fr 24px;
  padding: 15px;
  height: 100%;
`;

const gradient = keyframes`
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
`;

const Progress = styled.div`
  background: linear-gradient(
    90deg,
    #1bbcff -24.77%,
    #a259ff 32.63%,
    #ea7600 91.77%
  );
  background-size: 300% 100%;
  animation: ${gradient} 2s ease infinite;
  border-radius: 54px;
  height: 8px;
  width: 142px;
`;

const Loader = styled.div`
  align-self: center;
  margin: 0 auto;
  text-align: center;
  p {
    margin: 0 0 12px 0;
    font-size: 13px;
    font-weight: 600;
  }
`;

const Button = styled.button`
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  background: linear-gradient(
    90deg,
    #1bbcff -24.77%,
    #a259ff 32.63%,
    #ea7600 91.77%
  );
  border-radius: 8px;
  padding: 8px;
  border: 0;
  width: 100%;
  height: 48px;
  color: #fff;
  position: relative;
  animation: ${gradient} 3s ease infinite;
  &:hover {
    background-size: 400% 100%;
    &::after {
      background-size: 400% 100%;
      animation: ${gradient} 3s ease infinite;
    }
  }
  &:active {
    top: 1px;
  }
  &::after {
    content: '';
    position: absolute;
    left: 10px;
    top: 13px;
    background: linear-gradient(
      90deg,
      #1bbcff -24.77%,
      #a259ff 32.63%,
      #ea7600 91.77%
    );
    opacity: 0.7;
    filter: blur(16px);
    border-radius: 8px;
    width: 191px;
    height: 42px;
    z-index: -1;
  }
  .icon {
    background: rgba(255, 255, 255, 0.22);
    border-radius: 3.5px;
    position: relative;
    &::after {
      content: '';
      position: absolute;
      top: 50%;
      right: -2.5px;
      margin-top: -2.5px;
      width: 5px;
      height: 5px;
      transform: rotate(45deg);
      background-color: #fff;
    }
    &::before {
      content: '';
      position: absolute;
      top: 50%;
      right: -10px;
      margin-top: 0px;
      width: 10px;
      height: 1px;
      background-color: #fff;
    }
    &:first-child {
      padding: 7px 10px 7px 11px;
      svg {
        width: 12px;
        height: 19px;
      }
    }
    &:last-child {
      padding: 6px 7px 8px;
      svg {
        width: 19px;
        height: 19px;
      }
      &::after {
        left: -2.5px;
      }
      &::before {
        left: -10px;
      }
    }
  }
`;

export default Home;
