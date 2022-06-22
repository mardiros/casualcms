Feature: As a user, I can create and publish new pages

  Scenario: Create my first web page after login
    Given anonymous user on the admin page
    Then I see the login page
    When I fill the field "username" with "alice"
    And I fill the field "password" with "secret"
    And I click on the "Sign In" button
    Then I see the text "Create my first page"
    When I click on the "Create my first page" link
    Then I see the text "Available Templates"
    And I see the text "blog:HomePage"

  Scenario: Create new page
    Given user on the admin page
    When I click on the "Create my first page" link
    Then I see the text "Available Templates"
    And I see the text "blog:HomePage"
