<script lang="ts">
	export let name: string;
	export let nameCompletelyInvalid = false;
	export let placeholder = 'Name';
	export let mini = true;
</script>

<input
	type="text"
	{placeholder}
	class:mini
	bind:value={name}
	on:focusout={() => (nameCompletelyInvalid = name == undefined || name == '')}
	class:invalid={nameCompletelyInvalid}
/>
