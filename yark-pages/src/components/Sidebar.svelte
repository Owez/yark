<nav>
	<div class="sidebar card-border" />
</nav>

<style lang="scss">
	$fullwidth: 75px;
	$fullheight: 100vh;
	$gap: 1rem;

	nav {
		width: $fullwidth;
		height: $fullheight;
		display: flex;
		justify-content: center;
		align-items: center;
	}

	.sidebar {
		width: calc($fullwidth - $gap * 2);
		height: calc($fullheight - $gap * 1.5);
	}
</style>
