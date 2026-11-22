import { makeAutoObservable } from "mobx";
import React, { type ReactNode } from "react";

import { ConnectionEnum, type FigmaElement } from "../utils/interfaces";

export class RootStore {
	constructor() {
		makeAutoObservable(this);
	}

	url = "ws://localhost:1410";
	status = ConnectionEnum.CONNECTING;
	notAllowed = false;
	elements: FigmaElement[] = [];
	page_name = "";
	scaling = 1;

	setStatus(status: ConnectionEnum) {
		this.status = status;
	}

	setNotAllowed() {
		this.notAllowed = true;
	}

	setElements(elements: FigmaElement[]) {
		this.elements = elements;
	}

	setPageName(page_name: string) {
		this.page_name = page_name;
	}

	setScaling(scaling: number) {
		this.scaling = scaling;
	}
}

export const rootStore = new RootStore();

const StoreContext = React.createContext<RootStore | null>(null);

export const StoreProvider = ({ children }: { children: ReactNode }) => (
	<StoreContext.Provider value={rootStore}>{children}</StoreContext.Provider>
);

export const useStore = () => {
	const store = React.useContext(StoreContext);
	if (!store) {
		throw new Error("useStore must be used within a StoreProvider.");
	}
	return store;
};
