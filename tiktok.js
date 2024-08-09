const results = []

const commentList = document.querySelector(
	"[class*='-DivCommentListContainer']"
)

const loadReply = (commentItem) =>
	commentItem.querySelector("[class*='-PReplyActionText']")?.click()

const processComment = (commentItem) => {
	const avatar = commentItem
		.querySelector("[class*='-ImgAvatar']")
		?.getAttribute("src")
	const handle = commentItem
		.querySelector("[class*='-StyledLink-StyledUserLinkName']")
		?.getAttribute("href")
		?.replace("/@", "")
	const username = commentItem.querySelector(
		"[class*='-SpanUserNameText']"
	)?.textContent
	const commentLevel = commentItem
		.querySelector("[class*='-PCommentText']")
		?.getAttribute("data-e2e")
	const commentContent = commentItem.querySelector(
		"[class*='-PCommentText'] > span"
	)?.textContent
	const likesCount = commentItem.querySelector(
		"[class*='-SpanCount']"
	)?.textContent

	return {
		avatar,
		handle,
		username,
		commentLevel,
		commentContent,
		likesCount
	}
}

if (commentList) {
	const commentItems = commentList.querySelectorAll(
		"[class*='-DivCommentItemContainer']"
	)
	for (const commentItem of commentItems) {
		results.push(processComment(commentItem))
		loadReply(commentItem)
		const replyList = commentItem.querySelector(
			"[class*='-DivReplyContainer']"
		)

		if (replyList) {
			const replyItems = replyList.querySelectorAll(
				"[class*='-DivCommentContentContainer']"
			)
			for (const replyItem of replyItems) {
				results.push(processComment(replyItem))
			}
		}
	}
}

console.log(results)
console.log(results.length)
