/* oxlint-disable jsx-a11y/prefer-tag-over-role -- custom listbox styled like Figma menus; native select cannot be styled */
import {
	type KeyboardEvent,
	useEffect,
	useId,
	useLayoutEffect,
	useRef,
	useState,
} from "react";
import styled from "styled-components";

export interface SelectOption<T> {
	value: T;
	label: string;
}

interface SelectProps<T> {
	value: T;
	options: SelectOption<T>[];
	onChange: (value: T) => void;
	"aria-label"?: string;
}

const ITEM_HEIGHT = 24;
const MENU_PADDING = 8;
const VIEWPORT_GAP = 8;

/**
 * Dropdown styled after Figma's own: the menu opens over the trigger with the
 * selected item lined up on top of it, like the native Figma property menus.
 */
export function Select<T>({
	value,
	options,
	onChange,
	"aria-label": ariaLabel,
}: SelectProps<T>) {
	const id = useId();
	const triggerRef = useRef<HTMLButtonElement>(null);
	const menuRef = useRef<HTMLUListElement>(null);
	const [open, setOpen] = useState(false);
	const [active, setActive] = useState(0);
	const [position, setPosition] = useState({ top: 0, left: 0, width: 0 });

	const selectedIndex = Math.max(
		0,
		options.findIndex((o) => o.value === value),
	);
	const selected = options[selectedIndex];

	const openMenu = () => {
		setActive(selectedIndex);
		setOpen(true);
	};

	const close = (focusTrigger = true) => {
		setOpen(false);
		if (focusTrigger) triggerRef.current?.focus();
	};

	const choose = (index: number) => {
		const option = options[index];
		if (option) onChange(option.value);
		close();
	};

	// Place the menu so the selected item sits on the trigger, then clamp it
	// into the (small) plugin window.
	useLayoutEffect(() => {
		if (!open || !triggerRef.current) return;
		const rect = triggerRef.current.getBoundingClientRect();
		const menuHeight = options.length * ITEM_HEIGHT + MENU_PADDING * 2;
		let top =
			rect.top -
			MENU_PADDING -
			selectedIndex * ITEM_HEIGHT +
			(rect.height - ITEM_HEIGHT) / 2;
		const maxTop = window.innerHeight - menuHeight - VIEWPORT_GAP;
		top = Math.max(VIEWPORT_GAP, Math.min(top, maxTop));
		const width = Math.max(rect.width + 24, 96);
		const left = Math.min(
			rect.left - 24,
			window.innerWidth - width - VIEWPORT_GAP,
		);
		setPosition({ top, left: Math.max(VIEWPORT_GAP, left), width });
		menuRef.current?.focus();
	}, [open, options.length, selectedIndex]);

	useEffect(() => {
		if (!open) return;
		const onPointerDown = (e: PointerEvent) => {
			const target = e.target as Node;
			if (
				!menuRef.current?.contains(target) &&
				!triggerRef.current?.contains(target)
			) {
				setOpen(false);
			}
		};
		const onBlur = () => setOpen(false);
		document.addEventListener("pointerdown", onPointerDown);
		window.addEventListener("blur", onBlur);
		window.addEventListener("resize", onBlur);
		return () => {
			document.removeEventListener("pointerdown", onPointerDown);
			window.removeEventListener("blur", onBlur);
			window.removeEventListener("resize", onBlur);
		};
	}, [open]);

	const onTriggerKeyDown = (e: KeyboardEvent) => {
		if (["ArrowDown", "ArrowUp", "Enter", " "].includes(e.key)) {
			e.preventDefault();
			openMenu();
		}
	};

	const onMenuKeyDown = (e: KeyboardEvent) => {
		switch (e.key) {
			case "ArrowDown":
				e.preventDefault();
				setActive((i) => (i + 1) % options.length);
				break;
			case "ArrowUp":
				e.preventDefault();
				setActive((i) => (i - 1 + options.length) % options.length);
				break;
			case "Home":
				e.preventDefault();
				setActive(0);
				break;
			case "End":
				e.preventDefault();
				setActive(options.length - 1);
				break;
			case "Enter":
			case " ":
				e.preventDefault();
				choose(active);
				break;
			case "Escape":
			case "Tab":
				e.preventDefault();
				close();
				break;
		}
	};

	return (
		<>
			<Trigger
				ref={triggerRef}
				type="button"
				aria-haspopup="listbox"
				aria-expanded={open}
				aria-controls={open ? id : undefined}
				aria-label={ariaLabel}
				data-open={open || undefined}
				onClick={() => (open ? close() : openMenu())}
				onKeyDown={onTriggerKeyDown}
			>
				<span>{selected?.label}</span>
				<Chevron />
			</Trigger>
			{open && (
				<Menu
					ref={menuRef}
					id={id}
					role="listbox"
					tabIndex={-1}
					aria-activedescendant={`${id}-${active}`}
					onKeyDown={onMenuKeyDown}
					style={{
						top: position.top,
						left: position.left,
						minWidth: position.width,
					}}
				>
					{options.map((option, index) => (
						<Item
							key={String(option.value)}
							id={`${id}-${index}`}
							role="option"
							aria-selected={index === selectedIndex}
							data-active={index === active || undefined}
							onPointerMove={() => setActive(index)}
							onClick={() => choose(index)}
						>
							<span className="check">
								{index === selectedIndex && <Check />}
							</span>
							{option.label}
						</Item>
					))}
				</Menu>
			)}
		</>
	);
}

const Chevron = () => (
	<svg width="8" height="8" viewBox="0 0 8 8" aria-hidden="true">
		<path
			d="M1.5 3 4 5.5 6.5 3"
			fill="none"
			stroke="currentColor"
			strokeLinecap="round"
			strokeLinejoin="round"
		/>
	</svg>
);

const Check = () => (
	<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">
		<path
			d="m4.5 8.5 2.25 2.25L11.5 5.5"
			fill="none"
			stroke="currentColor"
			strokeWidth="1.2"
			strokeLinecap="round"
			strokeLinejoin="round"
		/>
	</svg>
);

const Trigger = styled.button`
	display: inline-flex;
	align-items: center;
	gap: 6px;
	height: 24px;
	padding: 0 6px 0 8px;
	font: inherit;
	font-size: 11px;
	color: var(--figma-color-text, #000);
	background: transparent;
	border: 1px solid transparent;
	border-radius: 5px;
	cursor: default;
	outline: none;

	svg {
		color: var(--figma-color-icon-secondary, rgba(0, 0, 0, 0.5));
	}

	&:hover,
	&[data-open] {
		border-color: var(--figma-color-border, #e6e6e6);
		svg {
			color: var(--figma-color-icon, rgba(0, 0, 0, 0.9));
		}
	}

	&:focus-visible {
		border-color: var(--figma-color-border-selected, #0d99ff);
		box-shadow: 0 0 0 1px var(--figma-color-border-selected, #0d99ff) inset;
	}
`;

const Menu = styled.ul`
	position: fixed;
	z-index: 100;
	margin: 0;
	padding: ${MENU_PADDING}px;
	list-style: none;
	font-size: 11px;
	color: var(--figma-color-text-menu, #fff);
	background: var(--figma-color-bg-menu, #1e1e1e);
	border-radius: 13px;
	box-shadow:
		0 0 0.5px rgba(0, 0, 0, 0.15),
		0 5px 12px rgba(0, 0, 0, 0.13),
		0 1px 3px rgba(0, 0, 0, 0.1);
	outline: none;
`;

const Item = styled.li`
	display: flex;
	align-items: center;
	height: ${ITEM_HEIGHT}px;
	padding-right: 16px;
	border-radius: 5px;
	white-space: nowrap;
	cursor: default;

	.check {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 24px;
		height: 100%;
	}

	&[data-active] {
		background: var(--figma-color-bg-menu-selected, #0d99ff);
		color: var(--figma-color-text-menu-selected, #fff);
	}
`;
