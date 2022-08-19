Feature: As a developper, I want a browser open with a session

  @dev
  Scenario: start an initialized session and wait
    Given user on the admin page
    And a "/home" page of type "blog:HomePage"
    And a "/home/cat" page of type "blog:CategoryPage"
    And a "/home/dog" page of type "blog:CategoryPage"
    And a "/home/cat/my-first-article" page of type "blog:BlogPage"
    And a "/home/dog/the-second-one" page of type "blog:BlogPage"
    And a "/home/dog/the-third-one" page of type "blog:BlogPage"
    And a "header" snippet of type "blog:HeaderSnippet"
    And a "127.0.0.1:6556" site with "/home" root page
    When I visit "/admin/pages?parent=/home"
    And I wait
