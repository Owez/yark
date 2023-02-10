<script lang="ts">
	export let name: string;
	export let nameCompletelyInvalid = false;
	export let placeholder = 'Name';
</script>

<input
	type="text"
	{placeholder}
	class="mini"
	bind:value={name}
	on:focusout={() => (nameCompletelyInvalid = name == undefined || name == '')}
	class:invalid={nameCompletelyInvalid}
/>
