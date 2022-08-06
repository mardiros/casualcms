Feature: As a user, I can navigate using the breadcrumb

  Scenario: use the breadcrumb to navigate throw the page list.
    Given user on the admin page
    And a "/home" page of type "blog:HomePage"
    And a "/home/cat" page of type "blog:CategoryPage"
    And a "/home/dog" page of type "blog:CategoryPage"
    And a "/home/cat/my-first-article" page of type "blog:BlogPage"
    And a "/home/dog/the-second-one" page of type "blog:BlogPage"
    And a "/home/dog/the-third-one" page of type "blog:BlogPage"
    When I visit "/admin/pages?parent=/home/cat/my-first-article"
    Then I see the breadcrumb "🏠 / home / cat / my-first-article"
    When I visit "/admin/pages?parent=/home/dog/the-second-one"
    Then I see the breadcrumb "🏠 / home / dog / the-second-one"
    When I click on the "dog" link
    Then I see the text "the-second-one"
    And I see the text "the-third-one"
    When I click on the "home" link
    Then I see the text "dog"
    And I see the text "cat"
