import { WEBUI_API_BASE_URL } from '$lib/constants';

export type ReferenceCapsuleContent = {
	title: string;
	summary: string;
	facts: string[];
	decisions: string[];
	constraints: string[];
	open_questions: string[];
	tags: string[];
};

export type ReferenceCapsule = ReferenceCapsuleContent & {
	id: string;
	user_id: string;
	source_chat_id: string;
	source_title: string;
	source_updated_at: number;
	source_hash: string;
	created_at: number;
	updated_at: number;
	source_exists: boolean;
	stale: boolean;
};

export type ReferenceCapsulePreview = ReferenceCapsuleContent & {
	existing_id: string | null;
	source_chat_id: string;
	source_title: string;
	source_updated_at: number;
	source_hash: string;
	generated: boolean;
};

const request = async (token: string, path: string, options: RequestInit = {}) => {
	let error: any = null;
	const response = await fetch(`${WEBUI_API_BASE_URL}/reference-capsules${path}`, {
		...options,
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`,
			...(options.headers ?? {})
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err?.detail ?? err;
			console.error(err);
			return null;
		});

	if (error) throw error;
	return response;
};

export const getReferenceCapsules = async (
	token: string,
	query = ''
): Promise<ReferenceCapsule[]> =>
	request(token, `/?query=${encodeURIComponent(query)}`, { method: 'GET' });

export const previewReferenceCapsule = async (
	token: string,
	sourceChatId: string,
	model?: string,
	regenerate = false
): Promise<ReferenceCapsulePreview> =>
	request(token, '/preview', {
		method: 'POST',
		body: JSON.stringify({
			source_chat_id: sourceChatId,
			model: model || undefined,
			regenerate
		})
	});

export const saveReferenceCapsule = async (
	token: string,
	preview: ReferenceCapsulePreview
): Promise<ReferenceCapsule> =>
	request(token, '/', {
		method: 'POST',
		body: JSON.stringify({
			source_chat_id: preview.source_chat_id,
			source_hash: preview.source_hash,
			title: preview.title,
			summary: preview.summary,
			facts: preview.facts,
			decisions: preview.decisions,
			constraints: preview.constraints,
			open_questions: preview.open_questions,
			tags: preview.tags
		})
	});

export const updateReferenceCapsule = async (
	token: string,
	id: string,
	content: ReferenceCapsuleContent
): Promise<ReferenceCapsule> =>
	request(token, `/${id}`, {
		method: 'PUT',
		body: JSON.stringify(content)
	});

export const deleteReferenceCapsule = async (token: string, id: string) =>
	request(token, `/${id}`, { method: 'DELETE' });
