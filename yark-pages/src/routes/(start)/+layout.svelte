<div class="header">
	<h1>Yark <span>1.3.0</span></h1>
</div>

<slot />

<style lang="scss">
	.header {
		display: flex;
		justify-content: center;
	}

	h1 {
		font-weight: 600;
		font-size: 20pt;
		margin:0;
		margin-top:1rem;
		margin-bottom:0.25rem;

		span {
			font-weight: normal;
			font-size: 12pt;
		}
	}
</style>
