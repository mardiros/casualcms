Feature: As a user, I can create and publish snippets

  Scenario: Create a header snippet
    Given user on the admin page
    And a "/home" page of type "blog:HomePage"
    And a "/home/cat" page of type "blog:CategoryPage"
    And a "/home/dog" page of type "blog:CategoryPage"
    When I visit "/admin/snippets/new"
    Then I see the text "Choose A Type Of Snippet"
    And I see the text "blog:HeaderSnippet"
    And I see the text "casualblog.models:FooterSnippet"
    When I click on the "blog:HeaderSnippet" link
    And I fill the field "slug" with "header"
    And I fill the field "title" with "Casual Blog"
    # First link
    And I click on the "Add Item" button
    And I fill the "second" field "title" with "Cat"
    And I fill the field "href" with "/home/cat"
    # Second link
    And I click on the "Add Item" button
    And I fill the "third" field "title" with "Dog"
    And I fill the "second" field "href" with "/home/dog"
    # Submit the form
    And I click on the "Submit" button
    Then I see the text "blog:HeaderSnippet"
    And I see the text "header"
    And I see the text "Edit"
    When I visit "/home"
    Then I see the text "Casual Blog"
    And I see the text "Cat"
    And I see the text "Dog"
    When I click on the "Cat" link
    Then I see the heading "Cat"
