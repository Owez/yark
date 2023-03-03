<script lang="ts">
	import { page } from '$app/stores';

	/**
	 * Checks if the name provided is the active archive route
	 * @param name Video category name to check
	 */
	function isActive(name: string, url: string): boolean {
		return url.endsWith(`/archive/${name}`);
	}

	/**
	 * Gets the button filepath for video category buttons depending on active state
	 * @param name Name of the button to get
	 * @param active Active state of the button (if it should be blue or not)
	 */
	function getVideoButtonFile(name: string, url: string): string {
		const prefix = `/img/btn${name}`;
		const suffix = '.svg';
		if (isActive(name, url)) {
			return `${prefix}_active${suffix}`;
		}
		return prefix + suffix;
	}

	$: videosFile = getVideoButtonFile('videos', $page.url.pathname);
	$: livestreamsFile = getVideoButtonFile('livestreams', $page.url.pathname);
	$: shortsFile = getVideoButtonFile('shorts', $page.url.pathname);
</script>

<nav>
	<div class="sidebar card-border">
		<div class="sidebar-list">
			<a href="/archive/videos" class="logo invis">Y</a>
			<div class="split" />
			<a href="/archive/videos">
				<img src={videosFile} alt="Videos" class="video-button" />
			</a>
			<a href="/archive/livestreams">
				<img src={livestreamsFile} alt="Livestreams" class="video-button" />
			</a>
			<a href="/archive/shorts">
				<img src={shortsFile} alt="Short" class="video-button" />
			</a>
		</div>
		<div class="sidebar-list">
			<div class="split" />
			<a href="/">
				<img src="/img/btnexit.svg" alt="Exit to menu" class="exit-button" />
			</a>
		</div>
	</div>
</nav>

<style lang="scss">
	$width: 50px;
	$gap: 1rem;
	$button-size: 30px;

	nav {
		height: 100vh;
		display: flex;
		justify-content: center;
		align-items: center;
		margin-left: $gap;
		margin-right: $gap;
	}

	.sidebar {
		height: calc(100vh - $gap * 2);
		display: flex;
		flex-direction: column;
		justify-content: space-between;
	}

	.sidebar-list {
		width: $width;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.logo {
		$size: $width;
		$padding-v: 0.2rem;

		width: $size;
		height: $size;
		display: flex;
		justify-content: center;
		align-items: center;
		font-weight: bold;
		padding-top: $padding-v;
		padding-bottom: $padding-v;
		font-size: 24px;
	}

	.split {
		width: $width * 0.65;
		height: 1px;
		background-color: lightgray;
	}

	@mixin button {
		$padding-h: calc(($width - $button-size) / 2);

		width: $button-size;
		height: $button-size;
		border-radius: 7.5px;
		padding-left: $padding-h;
		padding-right: $padding-h;
	}

	.video-button {
		@include button;

		margin-top: 1.25rem;
		margin-bottom: -0.25rem;
	}

	.exit-button {
		@include button;

		width: 20px;
		margin-top: 0.75rem;
		margin-bottom: 0.4rem;
	}
</style>
