<nav>
	<div class="sidebar card-border">
		<a href="/archive/videos" class="logo invis">Y</a>
		<div class="split"/>
		<a href="/archive/videos"><img src="/img/btnvideos.svg" alt="Videos" class="video-button"></a>
		<a href="/archive/livestreams"><img src="/img/btnlivestreams.svg" alt="Livestreams" class="video-button"></a>
	</div>
</nav>

<style lang="scss">
	$width: 50px;
	$gap: 1rem;

	nav {
		height: 100vh;
		display: flex;
		justify-content: center;
		align-items: center;
		margin-left: $gap;
		margin-right: $gap;
	}

	.sidebar {
		width: $width;
		height: calc(100vh - $gap * 2);
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
	
	.video-button {
		$size:30px;

		width: $size;
		height: $size;
		border-radius: 5px;
		margin-top: 1.25rem;
		margin-bottom: -0.25rem;
	}
</style>
