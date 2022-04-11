import { observer } from 'mobx-react-lite';
import React, { useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { MemoryRouter as Router, Route, Routes } from 'react-router-dom';
import styled from 'styled-components';
import slugify from 'slugify';

import { SocketProvider } from './utils/SocketProvider';

import { StoreProvider, useStore } from './store';
import HomeView from './views/Home';
import './style.css';

import * as process from 'process';
import EventEmitter from './shared/EventEmitter';
import { chunkData } from './utils/helpers';
import { useWebSocket } from './utils/use-websocket';

window['process'] = process;

const AppWrapper = styled.div`
  overflow: hidden;
`;

const App = observer(() => {
  const store = useStore();
  const { socket } = useWebSocket({
    url: store.url,
    onmessage: (e, ws) => {
      const data = JSON.parse(e.data);

      const sendElement = async (id) => {
        const frame: any = await EventEmitter.ask('frame', id);

        if (frame) {
          let chunks = chunkData(frame.data);

          for (const chunk of chunks) {
            ws.send(
              JSON.stringify({
                event: 'element_data',
                type: 'FILE_DATA',
                data: Array.from(chunk),
              })
            );
          }

          ws.send(
            JSON.stringify({
              event: 'element_data',
              type: 'FILE_END',
              name: `${slugify(frame.name)}-${(+frame.id.replace(
                ':',
                58
              )).toString(16)}`,
              width: frame.width,
              height: frame.height,
            })
          );

          chunks = [];
          delete frame.data;
        } else {
          ws.send(
            JSON.stringify({
              event: 'element_data',
              type: 'FILE_ERROR',
            })
          );
        }
      };

      if (data.event === 'get_element') {
        sendElement(data.id);
      } else if (data.event === 'not_allowed') {
        store.setNotAllowed();
      } else if (data.event === 'init') {
        EventEmitter.emit('get data');
      }
    },
  });

  useEffect(() => {
    if (socket) {
      EventEmitter.on('data', ({ elements, page_name }) => {
        store.setElements(elements);
        store.setPageName(page_name);

        socket.send(
          JSON.stringify({
            event: 'data',
            elements: elements || [],
            page_name,
          })
        );
      });
    }

    return () => {
      EventEmitter.remove('frames');
    };
  }, [socket]);

  return (
    <AppWrapper>
      <SocketProvider socket={socket}>
        <Router>
          <Routes>
            <Route path="/" element={<HomeView />} />
          </Routes>
        </Router>
      </SocketProvider>
    </AppWrapper>
  );
});

const root = createRoot(document.getElementById('app'));

root.render(
  <StoreProvider>
    <App />
  </StoreProvider>
);
