<script lang="ts">
	import './reset.css';
	import './global.scss';
	import { appWindow, PhysicalSize } from '@tauri-apps/api/window';
	import { Command } from '@tauri-apps/api/shell';

	/**
	 * Sets minimum window size via tauri to prevent uglyness
	 */
	async function setWindowBounds() {
		await appWindow.setMinSize(new PhysicalSize(1250, 700));
	}

	// Set window bounds for all pages
	setWindowBounds();

	// Launch the api and do it without awaiting
	const command = Command.sidecar('../../yark-api/dist/yark-api');
	command.execute();
</script>

<slot />
