import { makeAutoObservable } from 'mobx';
import React from 'react';

import { ConnectionEnum } from '../utils/interfaces';

export class RootStore {
  constructor() {
    makeAutoObservable(this);
  }

  url = 'ws://localhost:1410';
  status = ConnectionEnum.CONNECTING;
  notAllowed = false;
  elements = [];
  page_name = '';

  setStatus(status: ConnectionEnum) {
    this.status = status;
  }

  setNotAllowed() {
    this.notAllowed = true;
  }

  setElements(elements) {
    this.elements = elements;
  }

  setPageName(page_name) {
    this.page_name = page_name;
  }
}

export const rootStore = new RootStore();

const StoreContext = React.createContext<RootStore | null>(null);

export const StoreProvider = ({ children }) => (
  <StoreContext.Provider value={rootStore}>{children}</StoreContext.Provider>
);

export const useStore = () => {
  const store = React.useContext(StoreContext);
  if (!store) {
    throw new Error('useStore must be used within a StoreProvider.');
  }
  return store;
};
