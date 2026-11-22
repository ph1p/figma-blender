import { observer } from "mobx-react-lite";
import type { FunctionComponent } from "react";
import styled, { keyframes } from "styled-components";

import { BlenderLogo } from "../assets/BlenderLogo";
import { ElementIcon } from "../assets/ElementIcon";
import { FigmaLogo } from "../assets/FigmaLogo";
import { PageIcon } from "../assets/PageIcon";
import { ScalingIcon } from "../assets/ScalingIcon";
import { Select } from "../components/Select";
import EventEmitter from "../shared/EventEmitter";
import { useStore } from "../store";
import { ConnectionEnum } from "../utils/interfaces";

const SCALE_OPTIONS = [0.5, 0.75, 1, 2, 3].map((value) => ({
	value,
	label: `${value}x`,
}));

const FooterElement = () => (
	<Footer>
		<a
			href="https://ph1p.gumroad.com/l/figma-blender-addon"
			target="_blank"
			rel="noreferrer"
		>
			Get the Blender addon (free) ↗
		</a>
	</Footer>
);

const askForFrames = () => EventEmitter.emit("get elements");

const Home: FunctionComponent = observer(() => {
	const store = useStore();

	if (
		store.status === ConnectionEnum.CONNECTING ||
		store.notAllowed ||
		store.addonTooNew
	) {
		return (
			<Wrapper>
				<Loader>
					<p className="title">
						{store.addonTooNew
							? "Update this plugin"
							: store.notAllowed
								? "Already connected"
								: "Waiting for Blender…"}
					</p>
					<p className="hint">
						{store.addonTooNew
							? "The Blender addon is newer than this plugin."
							: store.notAllowed
								? "Only one plugin can connect at a time."
								: "Start the server in the Blender addon panel."}
					</p>
					{!store.addonTooNew && <Progress />}
				</Loader>
				<FooterElement />
			</Wrapper>
		);
	}

	return (
		<Wrapper>
			<Main>
				<Header>
					<Status>
						<span className="dot" />
						Connected to Blender
					</Status>
				</Header>
				<Section>
					<Row>
						<Label>
							<PageIcon className="icon" />
							Page
						</Label>
						<Value title={store.page_name}>{store.page_name}</Value>
					</Row>
					<Row>
						<Label>
							<ElementIcon className="icon" />
							Elements
						</Label>
						<Value>{store.elements.length}</Value>
					</Row>
					<Row>
						<Label>
							<ScalingIcon className="icon" />
							Image scale
						</Label>
						<Select
							aria-label="Image scale"
							value={store.scaling}
							options={SCALE_OPTIONS}
							onChange={(value) => store.setScaling(value)}
						/>
					</Row>
				</Section>
				<Button type="button" onClick={askForFrames}>
					<span className="icon">
						<FigmaLogo />
					</span>
					<span className="label">Update elements</span>
					<span className="icon">
						<BlenderLogo />
					</span>
				</Button>
			</Main>

			<FooterElement />
		</Wrapper>
	);
});

const brandGradient = `linear-gradient(
	90deg,
	#1bbcff -24.77%,
	#a259ff 32.63%,
	#ea7600 91.77%
)`;

const gradient = keyframes`
	0% { background-position: 0% 50%; }
	50% { background-position: 100% 50%; }
	100% { background-position: 0% 50%; }
`;

const pulse = keyframes`
	0% { box-shadow: 0 0 0 0 rgba(20, 174, 92, 0.5); }
	70% { box-shadow: 0 0 0 5px rgba(20, 174, 92, 0); }
	100% { box-shadow: 0 0 0 0 rgba(20, 174, 92, 0); }
`;

const Wrapper = styled.div`
	display: grid;
	grid-template-rows: 1fr auto;
	height: 100vh;
	padding: 12px 16px;
`;

const Main = styled.div`
	display: flex;
	flex-direction: column;
	gap: 12px;
`;

const Header = styled.header`
	display: flex;
	align-items: center;
	justify-content: space-between;
	height: 24px;
`;

const Status = styled.div`
	display: inline-flex;
	align-items: center;
	gap: 8px;
	font-size: 11px;
	font-weight: 550;
	.dot {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: var(--figma-color-bg-success, #14ae5c);
		animation: ${pulse} 2s ease-out infinite;
	}
`;

const Section = styled.div`
	display: flex;
	flex-direction: column;
	padding: 4px 0;
	border-top: 1px solid var(--figma-color-border, #e6e6e6);
	border-bottom: 1px solid var(--figma-color-border, #e6e6e6);
`;

const Row = styled.div`
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 8px;
	min-height: 32px;
`;

const Label = styled.div`
	display: flex;
	align-items: center;
	gap: 8px;
	font-size: 11px;
	color: var(--figma-color-text-secondary, rgba(0, 0, 0, 0.5));
	white-space: nowrap;
	.icon {
		width: 12px;
		height: 12px;
		path {
			fill: var(--figma-color-icon-secondary, rgba(0, 0, 0, 0.5));
			fill-opacity: 1;
		}
	}
`;

const Value = styled.div`
	padding-right: 8px;
	font-size: 11px;
	font-weight: 550;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
`;

const Footer = styled.footer`
	padding-top: 8px;
	font-size: 11px;
	text-align: center;
	a {
		color: var(--figma-color-text-tertiary, rgba(0, 0, 0, 0.3));
		text-decoration: none;
		&:hover {
			color: var(--figma-color-text-secondary, rgba(0, 0, 0, 0.5));
		}
	}
`;

const Loader = styled.div`
	align-self: center;
	display: flex;
	flex-direction: column;
	align-items: center;
	text-align: center;
	.title {
		margin: 0 0 4px;
		font-size: 13px;
		font-weight: 600;
	}
	.hint {
		margin: 0 0 16px;
		font-size: 11px;
		color: var(--figma-color-text-secondary, rgba(0, 0, 0, 0.5));
	}
`;

const Progress = styled.div`
	background: ${brandGradient};
	background-size: 300% 100%;
	animation: ${gradient} 2s ease infinite;
	border-radius: 999px;
	height: 4px;
	width: 120px;
`;

const Button = styled.button`
	position: relative;
	display: flex;
	align-items: center;
	gap: 8px;
	width: 100%;
	height: 40px;
	padding: 0 6px;
	font: inherit;
	font-size: 11px;
	font-weight: 600;
	color: #fff;
	background: ${brandGradient};
	background-size: 200% 100%;
	border: 0;
	border-radius: 8px;
	cursor: pointer;
	outline: none;
	transition:
		background-position 0.4s ease,
		transform 0.1s ease;

	&:hover {
		background-position: 100% 50%;
	}
	&:active {
		transform: scale(0.98);
	}
	&:focus-visible {
		box-shadow:
			0 0 0 2px var(--figma-color-bg, #fff),
			0 0 0 4px var(--figma-color-border-selected, #0d99ff);
	}

	.label {
		flex: 1;
		text-align: center;
	}

	.icon {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 28px;
		height: 28px;
		background: rgba(255, 255, 255, 0.2);
		border-radius: 6px;
		svg {
			width: 14px;
			height: 14px;
		}
	}
`;

export default Home;
