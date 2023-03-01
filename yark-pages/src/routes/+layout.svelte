<script lang="ts">
	import './reset.css';
	import './global.scss';
	import { appWindow, PhysicalSize } from '@tauri-apps/api/window';

	/**
	 * Sets minimum window size via tauri to prevent uglyness
	 */
	async function setWindowBounds() {
		await appWindow.setMinSize(new PhysicalSize(1250, 700));
	}

	// Set bounds for all pages
	setWindowBounds();
</script>

<slot />
