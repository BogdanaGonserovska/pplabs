#import articleservice
from articleservice import ArticleServiceManager, setUpFirstModerator
from model import ArticleVersionStatus

articleServiceManager = ArticleServiceManager()
setUpFirstModerator(articleServiceManager);

if (not articleServiceManager.userExists("BettyBoom")):
    createUser("BettyBoom", "Betty", "Blossom", "bet.bloss7@gmail.com", "b1l2o3s4s5o6m", "+84 0782538460")
if (not articleServiceManager.userExists("MickeyMouse")):
    createUser("MickeyMouse", "Mickey", "Dark", "mickey.dark9097@gmail.com", "MickeY123", "+54 7583752084")

editorUserToken = articleServiceManager.loginUser("BettyBoom", "b1l2o3s4s5o6m")
editorUser = articleServiceManager.getCurrentUser(editorUserToken)

moderatorUserToken = articleServiceManager.loginUser("Tom2", "ttttom")
moderatorUser = articleServiceManager.getCurrentUser(moderatorUserToken)

version = articleServiceManager.createVersion(editorUser, "New Article", "This article is about ...")
article = articleServiceManager.acceptVersion(moderatorUser, version.id)
editedArticleVersion = articleServiceManager.createVersion(editorUser, "Updated Article", "This article is not about ...", article.versionId)

article = articleServiceManager.acceptVersion(moderatorUser, editedArticleVersion.id)

otherEditedArticleVersion = articleServiceManager.createVersion(editorUser, "Updated Article in parralel", "This is quite long change and I'm not sure if my changes will be accepted ...", version.id)
#article = articleServiceManager.acceptVersion(moderatorUser, otherEditedArticleVersion.id)
article = articleServiceManager.declineVersion(moderatorUser, otherEditedArticleVersion.id, "Article was changed since you started your updates. Please merge your updates with the most recent version and resubmit")

searchText = "Betty Blossom"
list = articleServiceManager.findArticles(searchText)
print("Articles Search Text:", searchText)
for x in list:
    print(x.id, "|", x.name, "|", x.authorName, "|", x.publishDate)

articleId = list[0].id
article = articleServiceManager.getArticle(articleId)
print("== Article #", articleId, " ==") 
print("Author: ", article.authorName) 
print("Name: ", article.name) 
print("Text: ", article.text) 
print("Version ID: ", article.versionId) 


searchText = "Updated Article"
status: ArticleVersionStatus = 'declined'
articleVersions = articleServiceManager.findArticleVersions(status, "Updated Article")
print("Article Versions Search Text:", searchText, "| Status:", status)
for x in articleVersions:
    print(x.id, "|", x.name, "|", x.status, "|", x.authorName, "|", x.publishDate, "|", x.versionDate, "|", x.editorName, "|", x.moderatorName)

articleVersionId = articleVersions[len(articleVersions)-1].id
articleVersion = articleServiceManager.getArticleVersion(articleVersionId)
print("== Article Version #", articleVersionId, " ==") 
print("Editor Name: ", articleVersion.editorName) 
print("Original ID: ", articleVersion.originalId) 
print("Original Date: ", articleVersion.originalDate) 
print("Version ID: ", articleVersion.id) 
print("Version Date: ", articleVersion.versionDate) 
print("Version Status: ", articleVersion.status) 
print("Original Name: ", articleVersion.originalName) 
print("Updated Name: ", articleVersion.name) 
print("Original Text: ", articleVersion.originalText) 
print("Updated  Text: ", articleVersion.text) 

